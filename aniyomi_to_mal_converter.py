#!/usr/bin/env python3
"""
ANIYOMI TO MAL CONVERTER - Complete All-in-One Tool
Features: MAL ID generation, smart title matching, XML chunking, progress saving
Everything in one script - no separate files needed!
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import pandas as pd
import requests
import time
import os
import sys
import json
import re
from datetime import datetime
from difflib import SequenceMatcher
import traceback
from pathlib import Path

# Configuration
CONFIG = {
    "chunk_size": 200,
    "api_delay": 1.2,
    "timeout": 15,
    "retry_attempts": 3,
    "log_file": "aniyomi_converter.log",
    "progress_file": "conversion_progress.json",
    "failed_titles_file": "failed_titles.json",
    "max_search_results": 10,
    "min_similarity": 0.7,
    "exact_similarity": 0.9
}

class Logger:
    """Real-time logging system with both console and file output"""
    def __init__(self, log_file):
        self.log_file = Path(log_file)
        self.console_logs = []
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message, level="INFO"):
        if not isinstance(message, str):
            message = str(message)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        colors = {
            "INFO": "\033[94m",      # Blue
            "SUCCESS": "\033[92m",   # Green  
            "WARNING": "\033[93m",   # Yellow
            "ERROR": "\033[91m",     # Red
            "RESET": "\033[0m"       # Reset
        }

        try:
            if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
                color = colors.get(level, colors["RESET"])
                print(f"{color}{log_entry}{colors['RESET']}")
            else:
                print(log_entry)
        except:
            print(log_entry)

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
                f.flush()
        except:
            pass

        self.console_logs.append(log_entry)
        if len(self.console_logs) > 500:
            self.console_logs = self.console_logs[-250:]

class ProgressManager:
    """Save and restore progress to handle interruptions"""
    def __init__(self, progress_file, logger):
        self.progress_file = Path(progress_file)
        self.logger = logger
        self.data = self.load_progress()
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

    def load_progress(self):
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        raise ValueError("Invalid progress data format")
                    return data
            except Exception:
                pass

        return {
            "completed_entries": [],
            "failed_entries": [],
            "current_chunk": 0,
            "session_start": datetime.now().isoformat()
        }

    def save_progress(self):
        try:
            temp_file = self.progress_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            temp_file.replace(self.progress_file)
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.log(f"Failed to save progress: {e}", "WARNING")

    def add_completed(self, entry_id):
        if isinstance(entry_id, str) and entry_id not in self.data["completed_entries"]:
            self.data["completed_entries"].append(entry_id)
            self.save_progress()

    def add_failed(self, title, reason):
        if isinstance(title, str) and isinstance(reason, str):
            self.data["failed_entries"].append({
                "title": title,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            self.save_progress()

    def is_completed(self, entry_id):
        return isinstance(entry_id, str) and entry_id in self.data["completed_entries"]

    def get_stats(self):
        return {
            "completed": len(self.data["completed_entries"]),
            "failed": len(self.data["failed_entries"]),
            "total_processed": len(self.data["completed_entries"]) + len(self.data["failed_entries"])
        }

class TitleFixer:
    """Smart title matching and fixing system"""
    def __init__(self, logger):
        self.logger = logger
        self.failed_titles = []
        self.cache = {}

    def clean_title(self, title):
        if not title or pd.isna(title):
            return ""

        title = str(title).strip()
        if not title:
            return ""

        patterns = [
            r'\s*\([^)]*\)\s*',
            r'\s*\[[^\]]*\]\s*',
            r'\s*\{[^}]*\}\s*',
            r'\s*【[^】]*】\s*',
            r'\s*〈[^〉]*〉\s*',
        ]

        for pattern in patterns:
            title = re.sub(pattern, ' ', title)

        title = re.sub(r'\s+', ' ', title)
        title = re.sub(r'^[\s\-_]+|[\s\-_]+$', '', title)
        return title.strip()

    def similarity(self, a, b):
        if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
            return 0.0
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def generate_search_terms(self, title):
        if not title:
            return []

        search_terms = [title]
        cleaned = self.clean_title(title)
        if cleaned and cleaned != title:
            search_terms.append(cleaned)

        alphanumeric = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip()
        if alphanumeric and alphanumeric not in search_terms:
            search_terms.append(alphanumeric)

        transformations = [
            lambda t: t.replace(':', ''),
            lambda t: t.replace('-', ' '),
            lambda t: t.replace('_', ' '),
            lambda t: re.sub(r'\bthe\b', '', t, flags=re.I),
        ]

        for transform in transformations:
            try:
                transformed = transform(title).strip()
                if transformed and transformed not in search_terms:
                    search_terms.append(transformed)
            except:
                continue

        if any(ord(char) > 127 for char in title):
            words = title.split()
            if words:
                search_terms.append(words[0])

        unique_terms = []
        for term in search_terms:
            if term and term not in unique_terms:
                unique_terms.append(term)

        return unique_terms[:10]

    def search_mal_with_retry(self, search_term, api_type):
        cache_key = f"{api_type}_{search_term}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        for attempt in range(CONFIG["retry_attempts"]):
            try:
                url = f"https://api.jikan.moe/v4/{api_type}"
                params = {
                    "q": search_term,
                    "limit": CONFIG["max_search_results"],
                    "order_by": "score",
                    "sort": "desc"
                }

                resp = requests.get(url, params=params, timeout=CONFIG["timeout"])
                resp.raise_for_status()

                data = resp.json().get("data", [])
                self.cache[cache_key] = data
                return data

            except requests.exceptions.Timeout:
                self.logger.log(f"Timeout for '{search_term}' (attempt {attempt + 1})", "WARNING")
                if attempt < CONFIG["retry_attempts"] - 1:
                    time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as e:
                self.logger.log(f"API error for '{search_term}': {e}", "ERROR")
                if attempt < CONFIG["retry_attempts"] - 1:
                    time.sleep(CONFIG["api_delay"] * (attempt + 1))
            except Exception as e:
                self.logger.log(f"Unexpected error for '{search_term}': {e}", "ERROR")
                break

        return []

    def search_mal_fuzzy(self, title, is_anime=True):
        if not title or not isinstance(title, str):
            return None, None

        api_type = "anime" if is_anime else "manga"
        search_terms = self.generate_search_terms(title)

        best_match = None
        best_similarity = 0

        for i, search_term in enumerate(search_terms):
            if not search_term.strip():
                continue

            self.logger.log(f"Trying search term ({i+1}/{len(search_terms)}): '{search_term}'", "INFO")

            data = self.search_mal_with_retry(search_term, api_type)
            if not data:
                continue

            for item in data:
                try:
                    mal_title = item.get("title", "")
                    alternative_titles = []

                    if "titles" in item:
                        for title_obj in item["titles"]:
                            if isinstance(title_obj, dict) and "title" in title_obj:
                                alternative_titles.append(title_obj["title"])

                    all_titles = [mal_title] + alternative_titles

                    for check_title in all_titles:
                        if not check_title:
                            continue

                        similarity = self.similarity(check_title, title)

                        if similarity >= CONFIG["exact_similarity"]:
                            self.logger.log(f"Exact match: {check_title} (ID: {item['mal_id']}, similarity: {similarity:.3f})", "SUCCESS")
                            return str(item["mal_id"]), check_title

                        if similarity > best_similarity and similarity >= CONFIG["min_similarity"]:
                            best_match = (str(item["mal_id"]), check_title, similarity)
                            best_similarity = similarity

                except (KeyError, TypeError) as e:
                    self.logger.log(f"Invalid item structure: {e}", "WARNING")
                    continue

            time.sleep(CONFIG["api_delay"])

        if best_match:
            mal_id, mal_title, similarity = best_match
            self.logger.log(f"Fuzzy match: {mal_title} (ID: {mal_id}, similarity: {similarity:.3f})", "WARNING")
            return mal_id, mal_title

        self.failed_titles.append({
            "original_title": title,
            "cleaned_title": self.clean_title(title),
            "search_terms": search_terms,
            "type": "anime" if is_anime else "manga",
            "timestamp": datetime.now().isoformat()
        })

        return None, None

    def save_failed_titles(self, filename=None):
        if not self.failed_titles:
            return

        if filename is None:
            filename = CONFIG["failed_titles_file"]

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.failed_titles, f, indent=2, ensure_ascii=False)
            self.logger.log(f"Saved {len(self.failed_titles)} failed titles to {filename}", "WARNING")
        except Exception as e:
            self.logger.log(f"Failed to save failed titles: {e}", "ERROR")

class XMLChunker:
    """Built-in XML chunking functionality (replaces fast_mal_import.py)"""
    def __init__(self, logger):
        self.logger = logger

    def load_existing_mal_list(self, mal_xml_file, is_anime=False):
        """Load existing MAL XML and return existing IDs"""
        if not mal_xml_file or not os.path.exists(mal_xml_file):
            self.logger.log(f"No existing MAL file provided or found", "INFO")
            return set()

        try:
            tree = ET.parse(mal_xml_file)
            root = tree.getroot()

            existing_ids = set()
            id_tag = "anime_animedb_id" if is_anime else "manga_mangadb_id"
            entry_tag = "anime" if is_anime else "manga"

            for entry in root.findall(entry_tag):
                mal_id_elem = entry.find(id_tag)
                if mal_id_elem is not None:
                    existing_ids.add(mal_id_elem.text)

            self.logger.log(f"Found {len(existing_ids)} existing entries in MAL list", "INFO")
            return existing_ids

        except Exception as e:
            self.logger.log(f"Error loading existing MAL list: {e}", "WARNING")
            return set()

    def load_generated_xml(self, source_xml_file, is_anime=False):
        """Load the XML generated in Step 1"""
        if not os.path.exists(source_xml_file):
            self.logger.log(f"Source XML file not found: {source_xml_file}", "ERROR")
            return []

        try:
            tree = ET.parse(source_xml_file)
            root = tree.getroot()

            entries_data = []
            id_tag = "series_animedb_id" if is_anime else "series_mangadb_id"
            entry_tag = "anime" if is_anime else "manga"

            for entry in root.findall(entry_tag):
                mal_id_elem = entry.find(id_tag)
                title_elem = entry.find("series_title")

                if mal_id_elem is not None and title_elem is not None:
                    entries_data.append((mal_id_elem.text, title_elem.text))

            self.logger.log(f"Loaded {len(entries_data)} entries from {source_xml_file}", "SUCCESS")
            return entries_data

        except Exception as e:
            self.logger.log(f"Error loading generated XML: {e}", "ERROR")
            return []

    def create_import_entry(self, mal_id, mal_title, is_anime=False):
        """Create proper MAL import entry"""
        if is_anime:
            entry = ET.Element("anime")
            ET.SubElement(entry, "anime_animedb_id").text = str(mal_id)
            ET.SubElement(entry, "anime_title").text = str(mal_title)
            ET.SubElement(entry, "anime_num_episodes").text = "0"
            ET.SubElement(entry, "my_id").text = "0"
            ET.SubElement(entry, "my_watched_episodes").text = "0"
            ET.SubElement(entry, "my_start_date").text = "0000-00-00"
            ET.SubElement(entry, "my_finish_date").text = "0000-00-00"
            ET.SubElement(entry, "my_score").text = "0"
            ET.SubElement(entry, "my_storage").text = ""
            ET.SubElement(entry, "my_storage_value").text = "0"
            ET.SubElement(entry, "my_status").text = "Plan to Watch"
            ET.SubElement(entry, "my_comments").text = ""
            ET.SubElement(entry, "my_times_watched").text = "0"
            ET.SubElement(entry, "my_rewatch_value").text = ""
            ET.SubElement(entry, "my_priority").text = "Low"
            ET.SubElement(entry, "my_tags").text = ""
            ET.SubElement(entry, "my_rewatching").text = "NO"
            ET.SubElement(entry, "my_rewatching_ep").text = "0"
            ET.SubElement(entry, "my_discuss").text = "YES"
            ET.SubElement(entry, "my_sns").text = "default"
            ET.SubElement(entry, "update_on_import").text = "1"
        else:
            entry = ET.Element("manga")
            ET.SubElement(entry, "manga_mangadb_id").text = str(mal_id)
            ET.SubElement(entry, "manga_title").text = str(mal_title)
            ET.SubElement(entry, "manga_volumes").text = "0"
            ET.SubElement(entry, "manga_chapters").text = "0"
            ET.SubElement(entry, "my_id").text = "0"
            ET.SubElement(entry, "my_read_volumes").text = "0"
            ET.SubElement(entry, "my_read_chapters").text = "0"
            ET.SubElement(entry, "my_start_date").text = "0000-00-00"
            ET.SubElement(entry, "my_finish_date").text = "0000-00-00"
            ET.SubElement(entry, "my_score").text = "0"
            ET.SubElement(entry, "my_storage").text = ""
            ET.SubElement(entry, "my_retail_volumes").text = "0"
            ET.SubElement(entry, "my_status").text = "Plan to Read"
            ET.SubElement(entry, "my_comments").text = ""
            ET.SubElement(entry, "my_times_read").text = "0"
            ET.SubElement(entry, "my_tags").text = ""
            ET.SubElement(entry, "my_priority").text = "Low"
            ET.SubElement(entry, "my_reread_value").text = ""
            ET.SubElement(entry, "my_rereading").text = "NO"
            ET.SubElement(entry, "my_discuss").text = "YES"
            ET.SubElement(entry, "my_sns").text = "default"
            ET.SubElement(entry, "update_on_import").text = "1"

        return entry

    def create_chunks(self, source_xml_file, existing_mal_xml=None, is_anime=False):
        """Create upload-ready chunks from generated XML"""
        self.logger.log(f"Starting chunk creation for {'anime' if is_anime else 'manga'}", "INFO")

        # Load data
        entries_data = self.load_generated_xml(source_xml_file, is_anime)
        if not entries_data:
            return

        existing_ids = self.load_existing_mal_list(existing_mal_xml, is_anime) if existing_mal_xml else set()

        # Filter out existing entries
        new_entries = [(mal_id, title) for mal_id, title in entries_data if mal_id not in existing_ids]
        self.logger.log(f"New entries to add: {len(new_entries)}", "INFO")

        if not new_entries:
            self.logger.log("No new entries to process!", "WARNING")
            return

        # Process in chunks
        total_chunks = (len(new_entries) + CONFIG["chunk_size"] - 1) // CONFIG["chunk_size"]

        for chunk_num in range(total_chunks):
            start_idx = chunk_num * CONFIG["chunk_size"]
            end_idx = min(start_idx + CONFIG["chunk_size"], len(new_entries))
            chunk_entries = new_entries[start_idx:end_idx]

            self.logger.log(f"Creating chunk {chunk_num + 1}/{total_chunks} (entries {start_idx + 1}-{end_idx})", "INFO")

            # Create XML root
            chunk_root = ET.Element("myanimelist")

            # Create myinfo
            myinfo = ET.SubElement(chunk_root, "myinfo")
            ET.SubElement(myinfo, "user_id").text = "0"
            ET.SubElement(myinfo, "user_name").text = "Exported"
            ET.SubElement(myinfo, "user_export_type").text = "1" if is_anime else "2"
            ET.SubElement(myinfo, f"user_total_{'anime' if is_anime else 'manga'}").text = str(len(chunk_entries))

            # Add entries
            for mal_id, title in chunk_entries:
                entry = self.create_import_entry(mal_id, title, is_anime)
                chunk_root.append(entry)

            # Save chunk
            media_type = "anime" if is_anime else "manga"
            filename = f"mal_{media_type}_final_chunk_{chunk_num + 1:02d}.xml"

            try:
                xml_str = ET.tostring(chunk_root, encoding='unicode')
                dom = minidom.parseString(xml_str)
                pretty_xml = dom.toprettyxml(indent="\t")

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(pretty_xml)

                self.logger.log(f"Created: {filename} ({len(chunk_entries)} entries)", "SUCCESS")
            except Exception as e:
                self.logger.log(f"Error creating chunk {chunk_num + 1}: {e}", "ERROR")

        self.logger.log(f"Chunk creation complete: {total_chunks} files created", "SUCCESS")

class UnifiedConverter:
    """Main converter with all functionality built-in"""
    def __init__(self):
        self.logger = Logger(CONFIG["log_file"])
        self.progress = ProgressManager(CONFIG["progress_file"], self.logger)
        self.title_fixer = TitleFixer(self.logger)
        self.chunker = XMLChunker(self.logger)
        self._check_dependencies()

    def _check_dependencies(self):
        try:
            import pandas
            import requests
        except ImportError as e:
            self.logger.log(f"Missing required dependency: {e}", "ERROR")
            self.logger.log("Please install with: pip install pandas requests", "ERROR")
            sys.exit(1)

    def show_menu(self):
        print("\n" + "="*70)
        print("🚀 ANIYOMI TO MAL CONVERTER - All-in-One Edition")
        print("="*70)
        print("1. Generate MAL IDs from CSV (Step 1)")
        print("2. Create Import Chunks from XML (Step 2)")
        print("3. Full Process (Steps 1 + 2 combined)")
        print("4. Validate XML Files") 
        print("5. Show Conversion Logs")
        print("6. Show Progress Statistics")
        print("7. Clear Progress/Cache")
        print("8. Exit")
        print("="*70)

        stats = self.progress.get_stats()
        if stats["total_processed"] > 0:
            print(f"📊 Progress: {stats['completed']} completed, {stats['failed']} failed")
            print("-" * 70)

        while True:
            try:
                choice = input("Choose option (1-8): ").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    return choice
                print("❌ Invalid choice. Please enter a number between 1-8.")
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Goodbye!")
                sys.exit(0)

    def get_file_input(self, prompt, check_exists=True):
        while True:
            try:
                filepath = input(prompt).strip().strip('"').strip("'")
                if not filepath:
                    print("❌ Please enter a file path.")
                    continue

                if check_exists and not os.path.exists(filepath):
                    print(f"❌ File not found: {filepath}")
                    continue

                return filepath
            except (KeyboardInterrupt, EOFError):
                print("\n❌ Operation cancelled.")
                return None

    def generate_mal_ids(self):
        """Generate MAL IDs from CSV (Step 1)"""
        print("\n📁 MAL ID Generation Setup")
        print("-" * 40)

        csv_file = self.get_file_input("Enter CSV file path: ", check_exists=True)
        if not csv_file:
            return

        while True:
            media_type = input("Type (anime/manga): ").strip().lower()
            if media_type in ["anime", "manga"]:
                break
            print("❌ Please enter 'anime' or 'manga'")

        output_file = input("Output XML file name (press Enter for default): ").strip()
        if not output_file:
            output_file = f"mal_{media_type}_import.xml"
            print(f"ℹ️  Using default filename: {output_file}")

        self.logger.log(f"Starting MAL ID generation for {media_type}", "INFO")

        try:
            df = pd.read_csv(csv_file, usecols=[0, 1], header=None, names=["title", "type"])
            original_count = len(df)

            df = df[df["type"].str.lower() == media_type]
            df["title"] = df["title"].apply(self.title_fixer.clean_title)
            df = df[df["title"].str.len() > 0]
            df = df.drop_duplicates(subset=['title'])

            final_count = len(df)
            self.logger.log(f"Loaded CSV: {original_count} total, {final_count} {media_type} entries", "INFO")

            if final_count == 0:
                self.logger.log(f"No {media_type} entries found in CSV file", "ERROR")
                return

        except Exception as e:
            self.logger.log(f"Error reading CSV: {e}", "ERROR")
            return

        # Create XML structure
        root = ET.Element("myanimelist")
        myinfo = ET.SubElement(root, "myinfo")
        ET.SubElement(myinfo, "user_id").text = "0"
        ET.SubElement(myinfo, "user_name").text = "Exported"
        ET.SubElement(myinfo, "user_export_type").text = "1" if media_type == "anime" else "2"
        ET.SubElement(myinfo, f"user_total_{media_type}").text = str(final_count)

        # Process entries
        successful = 0
        skipped = 0
        failed = 0

        try:
            for idx, row in df.iterrows():
                title = row["title"]
                entry_key = f"{media_type}_{title}"

                if self.progress.is_completed(entry_key):
                    self.logger.log(f"⏭️  Skipping (already processed): {title}", "INFO")
                    skipped += 1
                    continue

                self.logger.log(f"Processing ({idx+1-skipped}/{final_count}): {title}", "INFO")

                mal_id, mal_title = self.title_fixer.search_mal_fuzzy(title, media_type == "anime")

                if mal_id and mal_title:
                    try:
                        if media_type == "anime":
                            entry = self._create_anime_entry(mal_id, mal_title)
                        else:
                            entry = self._create_manga_entry(mal_id, mal_title)

                        root.append(entry)
                        self.progress.add_completed(entry_key)
                        successful += 1
                        self.logger.log(f"✅ Added: {title} → {mal_title} (ID: {mal_id})", "SUCCESS")
                    except Exception as e:
                        self.logger.log(f"❌ Error creating entry for {title}: {e}", "ERROR")
                        self.progress.add_failed(title, f"XML creation error: {e}")
                        failed += 1
                else:
                    self.progress.add_failed(title, "No MAL match found")
                    failed += 1
                    self.logger.log(f"❌ Failed: {title}", "ERROR")

                if (idx + 1) % 10 == 0:
                    self.logger.log(f"📊 Progress: {successful} successful, {failed} failed", "INFO")

        except KeyboardInterrupt:
            self.logger.log("⚠️  Process interrupted by user", "WARNING")
            print("\n⚠️  Processing interrupted. Progress has been saved.")

        # Save XML
        if successful > 0:
            try:
                xml_str = ET.tostring(root, encoding='unicode')
                dom = minidom.parseString(xml_str)
                pretty_xml = dom.toprettyxml(indent="  ")

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(pretty_xml)

                self.logger.log(f"✅ Saved XML: {output_file} ({successful} entries)", "SUCCESS")
            except Exception as e:
                self.logger.log(f"❌ Error saving XML: {e}", "ERROR")
                return

        if self.title_fixer.failed_titles:
            self.title_fixer.save_failed_titles()

        # Summary
        self.logger.log("="*50, "INFO")
        self.logger.log(f"📊 STEP 1 COMPLETE", "INFO")
        self.logger.log(f"✅ Successful: {successful}/{final_count}", "SUCCESS")
        self.logger.log(f"❌ Failed: {failed}/{final_count}", "ERROR")
        self.logger.log(f"⏭️  Skipped: {skipped} (already processed)", "INFO")

        if successful > 0:
            self.logger.log(f"📄 XML file created: {output_file}", "SUCCESS")
            self.logger.log(f"➡️  Ready for Step 2 (Create Import Chunks)", "INFO")

        self.logger.log("="*50, "INFO")
        input("\nPress Enter to continue...")

    def create_chunks(self):
        """Create import chunks from XML (Step 2)"""
        print("\n📦 Import Chunk Creation Setup")
        print("-" * 40)

        source_xml = self.get_file_input("Enter XML file with MAL IDs: ", check_exists=True)
        if not source_xml:
            return

        while True:
            media_type = input("Type (anime/manga): ").strip().lower()
            if media_type in ["anime", "manga"]:
                break
            print("❌ Please enter 'anime' or 'manga'")

        existing_xml = input("Enter your existing MAL export XML (optional, press Enter to skip): ").strip()
        if existing_xml and not os.path.exists(existing_xml):
            print("⚠️  Existing MAL file not found, proceeding without duplicate check")
            existing_xml = None

        self.chunker.create_chunks(source_xml, existing_xml, media_type == "anime")
        input("\nPress Enter to continue...")

    def full_process(self):
        """Run Steps 1 + 2 combined"""
        print("\n🚀 Full Process (Generate MAL IDs + Create Chunks)")
        print("-" * 50)

        csv_file = self.get_file_input("Enter CSV file path: ", check_exists=True)
        if not csv_file:
            return

        while True:
            media_type = input("Type (anime/manga): ").strip().lower()
            if media_type in ["anime", "manga"]:
                break
            print("❌ Please enter 'anime' or 'manga'")

        existing_xml = input("Enter your existing MAL export XML (optional, press Enter to skip): ").strip()
        if existing_xml and not os.path.exists(existing_xml):
            print("⚠️  Existing MAL file not found, proceeding without duplicate check")
            existing_xml = None

        # Step 1: Generate MAL IDs (internal)
        temp_xml = f"temp_mal_{media_type}_import.xml"

        self.logger.log("🎯 Starting Full Process", "INFO")
        self.logger.log("📋 Step 1: Generate MAL IDs", "INFO")

        # Load and process CSV (same as generate_mal_ids but automatic)
        try:
            df = pd.read_csv(csv_file, usecols=[0, 1], header=None, names=["title", "type"])
            df = df[df["type"].str.lower() == media_type]
            df["title"] = df["title"].apply(self.title_fixer.clean_title)
            df = df[df["title"].str.len() > 0].drop_duplicates(subset=['title'])

            root = ET.Element("myanimelist")
            myinfo = ET.SubElement(root, "myinfo")
            ET.SubElement(myinfo, "user_id").text = "0"
            ET.SubElement(myinfo, "user_name").text = "Exported"
            ET.SubElement(myinfo, "user_export_type").text = "1" if media_type == "anime" else "2"
            ET.SubElement(myinfo, f"user_total_{media_type}").text = str(len(df))

            successful = 0

            for idx, row in df.iterrows():
                title = row["title"]
                self.logger.log(f"Processing ({idx+1}/{len(df)}): {title}", "INFO")

                mal_id, mal_title = self.title_fixer.search_mal_fuzzy(title, media_type == "anime")

                if mal_id and mal_title:
                    if media_type == "anime":
                        entry = self._create_anime_entry(mal_id, mal_title)
                    else:
                        entry = self._create_manga_entry(mal_id, mal_title)

                    root.append(entry)
                    successful += 1
                    self.logger.log(f"✅ Added: {title} → {mal_title} (ID: {mal_id})", "SUCCESS")
                else:
                    self.logger.log(f"❌ Failed: {title}", "ERROR")

            # Save temp XML
            if successful > 0:
                xml_str = ET.tostring(root, encoding='unicode')
                dom = minidom.parseString(xml_str)
                pretty_xml = dom.toprettyxml(indent="  ")

                with open(temp_xml, 'w', encoding='utf-8') as f:
                    f.write(pretty_xml)

                self.logger.log(f"✅ Step 1 Complete: {successful} entries processed", "SUCCESS")

                # Step 2: Create chunks
                self.logger.log("📦 Step 2: Create Import Chunks", "INFO")
                self.chunker.create_chunks(temp_xml, existing_xml, media_type == "anime")

                # Clean up temp file
                try:
                    os.remove(temp_xml)
                except:
                    pass

                self.logger.log("🎉 Full process complete!", "SUCCESS")
            else:
                self.logger.log("❌ No successful entries, cannot proceed to chunking", "ERROR")

        except Exception as e:
            self.logger.log(f"Error in full process: {e}", "ERROR")

        if self.title_fixer.failed_titles:
            self.title_fixer.save_failed_titles()

        input("\nPress Enter to continue...")

    def _create_manga_entry(self, mal_id, mal_title):
        manga = ET.Element("manga")
        ET.SubElement(manga, "series_mangadb_id").text = str(mal_id)
        ET.SubElement(manga, "series_title").text = str(mal_title)
        ET.SubElement(manga, "series_type").text = "Manga"
        ET.SubElement(manga, "series_chapters").text = "0"
        ET.SubElement(manga, "series_volumes").text = "0"
        ET.SubElement(manga, "my_read_chapters").text = "0"
        ET.SubElement(manga, "my_read_volumes").text = "0"
        ET.SubElement(manga, "my_start_date").text = "0000-00-00"
        ET.SubElement(manga, "my_finish_date").text = "0000-00-00"
        ET.SubElement(manga, "my_score").text = "0"
        ET.SubElement(manga, "my_status").text = "2"
        ET.SubElement(manga, "update_on_import").text = "1"
        return manga

    def _create_anime_entry(self, mal_id, mal_title):
        anime = ET.Element("anime")
        ET.SubElement(anime, "series_animedb_id").text = str(mal_id)
        ET.SubElement(anime, "series_title").text = str(mal_title)
        ET.SubElement(anime, "series_type").text = "TV"
        ET.SubElement(anime, "series_episodes").text = "0"
        ET.SubElement(anime, "my_watched_episodes").text = "0"
        ET.SubElement(anime, "my_start_date").text = "0000-00-00"
        ET.SubElement(anime, "my_finish_date").text = "0000-00-00"
        ET.SubElement(anime, "my_score").text = "0"
        ET.SubElement(anime, "my_status").text = "2"
        ET.SubElement(anime, "update_on_import").text = "1"
        return anime

    def show_logs(self):
        print("\n" + "="*70)
        print("📋 RECENT CONVERSION LOGS")
        print("="*70)

        if os.path.exists(CONFIG["log_file"]):
            try:
                with open(CONFIG["log_file"], 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if lines:
                    print(f"Showing last {min(50, len(lines))} lines:")
                    print("-" * 70)
                    for line in lines[-50:]:
                        print(line.strip())
                else:
                    print("Log file is empty.")
            except Exception as e:
                print(f"❌ Error reading log file: {e}")
        else:
            print("ℹ️  No log file found.")

        input("\nPress Enter to continue...")

    def show_progress_stats(self):
        print("\n" + "="*70)
        print("📊 PROGRESS STATISTICS")
        print("="*70)

        stats = self.progress.get_stats()
        print(f"✅ Completed entries: {stats['completed']}")
        print(f"❌ Failed entries: {stats['failed']}")
        print(f"📊 Total processed: {stats['total_processed']}")

        if stats['total_processed'] > 0:
            success_rate = (stats['completed'] / stats['total_processed']) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")

        if self.progress.data['failed_entries']:
            print("\n❌ Recent failed entries:")
            print("-" * 40)
            for entry in self.progress.data['failed_entries'][-10:]:
                print(f"• {entry['title']} - {entry['reason']}")

        if 'session_start' in self.progress.data:
            print(f"\n🕒 Session started: {self.progress.data['session_start']}")

        input("\nPress Enter to continue...")

    def clear_progress(self):
        print("\n⚠️  This will delete all progress and cache files:")
        print(f"• {CONFIG['progress_file']}")
        print(f"• {CONFIG['log_file']}")
        print(f"• {CONFIG['failed_titles_file']}")

        confirm = input("\nAre you sure? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ Operation cancelled.")
            return

        files_to_remove = [CONFIG["progress_file"], CONFIG["log_file"], CONFIG["failed_titles_file"]]
        removed_count = 0

        for file in files_to_remove:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"✅ Removed: {file}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove {file}: {e}")

        if removed_count > 0:
            print(f"\n🧹 Cache cleared! Removed {removed_count} files.")
        else:
            print("\nℹ️  No cache files found to remove.")

        input("Press Enter to continue...")

    def run(self):
        try:
            self.logger.log("Aniyomi to MAL Converter All-in-One started", "INFO")

            while True:
                try:
                    choice = self.show_menu()

                    if choice == "1":
                        self.generate_mal_ids()
                    elif choice == "2":
                        self.create_chunks()
                    elif choice == "3":
                        self.full_process()
                    elif choice == "4":
                        xml_file = self.get_file_input("Enter XML file to validate: ")
                        if xml_file:
                            print("ℹ️  XML validation feature coming soon...")
                            input("Press Enter to continue...")
                    elif choice == "5":
                        self.show_logs()
                    elif choice == "6":
                        self.show_progress_stats()
                    elif choice == "7":
                        self.clear_progress()
                    elif choice == "8":
                        self.logger.log("Exiting converter", "INFO")
                        print("\n👋 Thank you for using Aniyomi to MAL Converter!")
                        break

                except KeyboardInterrupt:
                    print("\n\n⚠️  Operation interrupted. Your progress has been saved.")
                    choice = input("Do you want to exit? (y/n): ").lower().strip()
                    if choice in ['y', 'yes']:
                        break
                except Exception as e:
                    self.logger.log(f"Unexpected error in menu: {e}", "ERROR")
                    print(f"\n❌ An error occurred: {e}")
                    input("Press Enter to continue...")

        except Exception as e:
            self.logger.log(f"Critical error: {e}", "ERROR")
            print(f"\n💥 Critical error: {e}")
        finally:
            self.logger.log("Converter session ended", "INFO")

if __name__ == "__main__":
    try:
        converter = UnifiedConverter()
        converter.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Failed to start converter: {e}")
        print("Make sure you have installed: pip install pandas requests")
        sys.exit(1)
