#!/usr/bin/env python3
"""
ENHANCED ANIYOMI TO MAL CONVERTER - Master Tool v2.0
Features: Real-time logs, progress saving, smart title fixer, comprehensive error handling
Author: Enhanced with bulletproof error handling and improved performance
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

# Configuration with validation
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

        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message, level="INFO"):
        """Log message with timestamp and color coding"""
        if not isinstance(message, str):
            message = str(message)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        # Print to console with colors (with fallback for non-terminal environments)
        colors = {
            "INFO": "\033[94m",      # Blue
            "SUCCESS": "\033[92m",   # Green  
            "WARNING": "\033[93m",   # Yellow
            "ERROR": "\033[91m",     # Red
            "RESET": "\033[0m"       # Reset
        }

        try:
            if sys.stdout.isatty():  # Only use colors if terminal supports it
                color = colors.get(level, colors["RESET"])
                print(f"{color}{log_entry}{colors['RESET']}")
            else:
                print(log_entry)
        except AttributeError:
            # Fallback for environments without isatty()
            print(log_entry)

        # Save to file with error handling
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
                f.flush()  # Ensure immediate write
        except (IOError, OSError) as e:
            print(f"Warning: Could not write to log file: {e}")

        # Keep recent console logs (memory management)
        self.console_logs.append(log_entry)
        if len(self.console_logs) > 500:  # Increased buffer size
            self.console_logs = self.console_logs[-250:]  # Keep last 250

class ProgressManager:
    """Save and restore progress to handle interruptions"""
    def __init__(self, progress_file, logger):
        self.progress_file = Path(progress_file)
        self.logger = logger
        self.data = self.load_progress()

        # Ensure progress directory exists
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

    def load_progress(self):
        """Load progress from file with error recovery"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validate data structure
                    if not isinstance(data, dict):
                        raise ValueError("Invalid progress data format")
                    return data
            except (json.JSONDecodeError, ValueError, IOError) as e:
                print(f"Warning: Could not load progress file ({e}). Starting fresh.")

        return {
            "completed_entries": [],
            "failed_entries": [],
            "current_chunk": 0,
            "session_start": datetime.now().isoformat()
        }

    def save_progress(self):
        """Save progress with atomic write to prevent corruption"""
        try:
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.progress_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Atomic rename
            temp_file.replace(self.progress_file)
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.log(f"Failed to save progress: {e}", "WARNING")
            else:
                print(f"Warning: Failed to save progress: {e}")

    def add_completed(self, entry_id):
        """Add completed entry with duplicate check"""
        if isinstance(entry_id, str) and entry_id not in self.data["completed_entries"]:
            self.data["completed_entries"].append(entry_id)
            self.save_progress()

    def add_failed(self, title, reason):
        """Add failed entry with validation"""
        if isinstance(title, str) and isinstance(reason, str):
            self.data["failed_entries"].append({
                "title": title,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            self.save_progress()

    def is_completed(self, entry_id):
        """Check if entry was already processed"""
        return isinstance(entry_id, str) and entry_id in self.data["completed_entries"]

    def get_stats(self):
        """Get progress statistics"""
        return {
            "completed": len(self.data["completed_entries"]),
            "failed": len(self.data["failed_entries"]),
            "total_processed": len(self.data["completed_entries"]) + len(self.data["failed_entries"])
        }

class TitleFixer:
    """Smart title matching and fixing system with improved algorithms"""
    def __init__(self, logger):
        self.logger = logger
        self.failed_titles = []
        self.cache = {}  # Simple cache to avoid repeated API calls

    def clean_title(self, title):
        """Clean title for better matching with comprehensive rules"""
        if not title or pd.isna(title):
            return ""

        title = str(title).strip()
        if not title:
            return ""

        # Remove common extra text patterns
        patterns = [
            r'\s*\([^)]*\)\s*',     # Remove parentheses
            r'\s*\[[^\]]*\]\s*',   # Remove brackets
            r'\s*\{[^}]*\}\s*',     # Remove braces
            r'\s*【[^】]*】\s*',        # Remove Japanese brackets
            r'\s*〈[^〉]*〉\s*',        # Remove angle brackets
        ]

        for pattern in patterns:
            title = re.sub(pattern, ' ', title)

        # Clean up spacing and special characters
        title = re.sub(r'\s+', ' ', title)  # Multiple spaces to single
        title = re.sub(r'^[\s\-_]+|[\s\-_]+$', '', title)  # Trim special chars

        return title.strip()

    def similarity(self, a, b):
        """Calculate similarity with input validation"""
        if not isinstance(a, str) or not isinstance(b, str):
            return 0.0
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def generate_search_terms(self, title):
        """Generate comprehensive list of search terms"""
        if not title:
            return []

        search_terms = []

        # Original title
        search_terms.append(title)

        # Cleaned version
        cleaned = self.clean_title(title)
        if cleaned and cleaned != title:
            search_terms.append(cleaned)

        # Alphanumeric only
        alphanumeric = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip()
        if alphanumeric and alphanumeric not in search_terms:
            search_terms.append(alphanumeric)

        # Common transformations
        transformations = [
            lambda t: t.replace(':', ''),           # Remove colons
            lambda t: t.replace('-', ' '),          # Replace dashes
            lambda t: t.replace('_', ' '),          # Replace underscores  
            lambda t: re.sub(r'\bthe\b', '', t, flags=re.I),  # Remove "the"
        ]

        for transform in transformations:
            try:
                transformed = transform(title).strip()
                if transformed and transformed not in search_terms:
                    search_terms.append(transformed)
            except Exception:
                continue

        # Japanese/Unicode handling
        if any(ord(char) > 127 for char in title):
            words = title.split()
            if words:
                search_terms.append(words[0])  # First word only

        # Remove duplicates while preserving order
        unique_terms = []
        for term in search_terms:
            if term and term not in unique_terms:
                unique_terms.append(term)

        return unique_terms[:10]  # Limit search terms

    def search_mal_with_retry(self, search_term, api_type):
        """Search MAL API with retry logic and caching"""
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
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.RequestException as e:
                self.logger.log(f"API error for '{search_term}': {e}", "ERROR")
                if attempt < CONFIG["retry_attempts"] - 1:
                    time.sleep(CONFIG["api_delay"] * (attempt + 1))
            except Exception as e:
                self.logger.log(f"Unexpected error for '{search_term}': {e}", "ERROR")
                break

        return []

    def search_mal_fuzzy(self, title, is_anime=True):
        """Search MAL with multiple strategies and improved matching"""
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

            # Find best match from results
            for item in data:
                try:
                    mal_title = item.get("title", "")
                    alternative_titles = []

                    # Include alternative titles if available
                    if "titles" in item:
                        for title_obj in item["titles"]:
                            if isinstance(title_obj, dict) and "title" in title_obj:
                                alternative_titles.append(title_obj["title"])

                    all_titles = [mal_title] + alternative_titles

                    for check_title in all_titles:
                        if not check_title:
                            continue

                        similarity = self.similarity(check_title, title)

                        # Exact match - return immediately
                        if similarity >= CONFIG["exact_similarity"]:
                            self.logger.log(f"Exact match: {check_title} (ID: {item['mal_id']}, similarity: {similarity:.3f})", "SUCCESS")
                            return str(item["mal_id"]), check_title

                        # Track best match
                        if similarity > best_similarity and similarity >= CONFIG["min_similarity"]:
                            best_match = (str(item["mal_id"]), check_title, similarity)
                            best_similarity = similarity

                except (KeyError, TypeError) as e:
                    self.logger.log(f"Invalid item structure: {e}", "WARNING")
                    continue

            # Rate limiting
            time.sleep(CONFIG["api_delay"])

        # Return best match if found
        if best_match:
            mal_id, mal_title, similarity = best_match
            self.logger.log(f"Fuzzy match: {mal_title} (ID: {mal_id}, similarity: {similarity:.3f})", "WARNING")
            return mal_id, mal_title

        # If all searches failed, add to failed list
        self.failed_titles.append({
            "original_title": title,
            "cleaned_title": self.clean_title(title),
            "search_terms": search_terms,
            "type": "anime" if is_anime else "manga",
            "timestamp": datetime.now().isoformat()
        })

        return None, None

    def save_failed_titles(self, filename=None):
        """Save failed titles for manual review"""
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

class XMLValidator:
    """Validate XML structure before import with comprehensive checks"""
    def __init__(self, logger):
        self.logger = logger

    def validate_mal_xml(self, xml_file, is_anime=True):
        """Validate XML structure with detailed reporting"""
        if not os.path.exists(xml_file):
            self.logger.log(f"XML file not found: {xml_file}", "ERROR")
            return False

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Check root element
            if root.tag != "myanimelist":
                self.logger.log(f"Invalid root tag: expected 'myanimelist', got '{root.tag}'", "ERROR")
                return False

            # Check myinfo section
            myinfo = root.find("myinfo")
            if myinfo is None:
                self.logger.log("Missing myinfo section", "ERROR")
                return False

            # Validate myinfo fields
            required_myinfo_fields = ["user_id", "user_name", "user_export_type"]
            for field in required_myinfo_fields:
                elem = myinfo.find(field)
                if elem is None or not elem.text:
                    self.logger.log(f"Missing or empty myinfo field: {field}", "ERROR")
                    return False

            # Check entries
            entry_tag = "anime" if is_anime else "manga"
            id_tag = f"series_{'anime' if is_anime else 'manga'}db_id"

            entries = root.findall(entry_tag)
            if not entries:
                self.logger.log(f"No {entry_tag} entries found", "WARNING")
                return False

            # Validate each entry
            errors = 0
            warnings = 0

            for i, entry in enumerate(entries):
                # Check required fields
                mal_id = entry.find(id_tag)
                title = entry.find("series_title")
                update_flag = entry.find("update_on_import")

                if mal_id is None or not mal_id.text:
                    self.logger.log(f"Entry {i+1}: Missing MAL ID", "ERROR")
                    errors += 1
                elif not mal_id.text.isdigit():
                    self.logger.log(f"Entry {i+1}: Invalid MAL ID format: {mal_id.text}", "ERROR")
                    errors += 1

                if title is None or not title.text:
                    self.logger.log(f"Entry {i+1}: Missing title", "ERROR")
                    errors += 1

                if update_flag is None or update_flag.text != "1":
                    self.logger.log(f"Entry {i+1}: update_on_import not set to 1", "WARNING")
                    warnings += 1

            # Summary
            if errors > 0:
                self.logger.log(f"XML validation failed: {errors} errors, {warnings} warnings", "ERROR")
                return False
            else:
                self.logger.log(f"XML validation passed: {len(entries)} entries, {warnings} warnings", "SUCCESS")
                return True

        except ET.ParseError as e:
            self.logger.log(f"XML parsing error: {e}", "ERROR")
            return False
        except Exception as e:
            self.logger.log(f"Validation error: {e}", "ERROR")
            return False

class MasterConverter:
    """Main converter with all enhanced features and error handling"""
    def __init__(self):
        self.logger = Logger(CONFIG["log_file"])
        self.progress = ProgressManager(CONFIG["progress_file"], self.logger)
        self.title_fixer = TitleFixer(self.logger)
        self.validator = XMLValidator(self.logger)

        # Check dependencies
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required dependencies are available"""
        try:
            import pandas
            import requests
        except ImportError as e:
            self.logger.log(f"Missing required dependency: {e}", "ERROR")
            self.logger.log("Please install with: pip install pandas requests", "ERROR")
            sys.exit(1)

    def show_menu(self):
        """Interactive menu system with improved formatting"""
        print("\n" + "="*70)
        print("🚀 ANIYOMI TO MAL CONVERTER - Enhanced Edition v2.0")
        print("="*70)
        print("1. Generate MAL IDs from CSV (Step 1)")
        print("2. Create Import Chunks (Step 2) - Use fast_mal_import.py")
        print("3. Validate XML Files") 
        print("4. Show Conversion Logs")
        print("5. Show Progress Statistics")
        print("6. Clear Progress/Cache")
        print("7. Exit")
        print("="*70)

        stats = self.progress.get_stats()
        if stats["total_processed"] > 0:
            print(f"📊 Progress: {stats['completed']} completed, {stats['failed']} failed")
            print("-" * 70)

        while True:
            try:
                choice = input("Choose option (1-7): ").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7']:
                    return choice
                print("❌ Invalid choice. Please enter a number between 1-7.")
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Goodbye!")
                sys.exit(0)

    def get_file_input(self, prompt, check_exists=True):
        """Get file input with validation"""
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
        """Enhanced MAL ID generation with comprehensive error handling"""
        print("\n📁 MAL ID Generation Setup")
        print("-" * 40)

        # Get inputs with validation
        csv_file = self.get_file_input("Enter CSV file path: ", check_exists=True)
        if not csv_file:
            return

        while True:
            media_type = input("Type (anime/manga): ").strip().lower()
            if media_type in ["anime", "manga"]:
                break
            print("❌ Please enter 'anime' or 'manga'")

        output_file = input("Output XML file name: ").strip()
        if not output_file:
            output_file = f"mal_{media_type}_import.xml"
            print(f"ℹ️  Using default filename: {output_file}")

        self.logger.log(f"Starting MAL ID generation for {media_type}", "INFO")
        self.logger.log(f"Input: {csv_file}, Output: {output_file}", "INFO")

        # Read and validate CSV
        try:
            df = pd.read_csv(csv_file, usecols=[0, 1], header=None, names=["title", "type"])
            original_count = len(df)

            # Filter and clean
            df = df[df["type"].str.lower() == media_type]
            df["title"] = df["title"].apply(self.title_fixer.clean_title)
            df = df[df["title"].str.len() > 0]  # Remove empty titles
            df = df.drop_duplicates(subset=['title'])  # Remove duplicates

            final_count = len(df)
            self.logger.log(f"Loaded CSV: {original_count} total, {final_count} {media_type} entries after filtering", "INFO")

            if final_count == 0:
                self.logger.log(f"No {media_type} entries found in CSV file", "ERROR")
                return

        except Exception as e:
            self.logger.log(f"Error reading CSV: {e}", "ERROR")
            self.logger.log(f"Full error: {traceback.format_exc()}", "ERROR")
            return

        # Create XML structure
        root = ET.Element("myanimelist")
        myinfo = ET.SubElement(root, "myinfo")
        ET.SubElement(myinfo, "user_id").text = "0"
        ET.SubElement(myinfo, "user_name").text = "Exported"
        ET.SubElement(myinfo, "user_export_type").text = "1" if media_type == "anime" else "2"
        ET.SubElement(myinfo, f"user_total_{media_type}").text = str(final_count)

        # Process entries with progress tracking
        successful = 0
        skipped = 0
        failed = 0

        self.logger.log("🚀 Starting processing...", "INFO")

        try:
            for idx, row in df.iterrows():
                title = row["title"]
                entry_key = f"{media_type}_{title}"

                # Skip if already processed
                if self.progress.is_completed(entry_key):
                    self.logger.log(f"⏭️  Skipping (already processed): {title}", "INFO")
                    skipped += 1
                    continue

                progress_msg = f"Processing ({idx+1-skipped}/{final_count}): {title}"
                self.logger.log(progress_msg, "INFO")

                # Get MAL ID with smart matching
                mal_id, mal_title = self.title_fixer.search_mal_fuzzy(title, media_type == "anime")

                if mal_id and mal_title:
                    # Create entry
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

                # Progress update every 10 entries
                if (idx + 1) % 10 == 0:
                    self.logger.log(f"📊 Progress: {successful} successful, {failed} failed", "INFO")

        except KeyboardInterrupt:
            self.logger.log("⚠️  Process interrupted by user", "WARNING")
            print("\n⚠️  Processing interrupted. Progress has been saved.")
        except Exception as e:
            self.logger.log(f"❌ Unexpected error during processing: {e}", "ERROR")
            self.logger.log(f"Full error: {traceback.format_exc()}", "ERROR")

        # Save XML if we have successful entries
        if successful > 0:
            try:
                self.logger.log("💾 Saving XML file...", "INFO")
                xml_str = ET.tostring(root, encoding='unicode')
                dom = minidom.parseString(xml_str)
                pretty_xml = dom.toprettyxml(indent="  ")

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(pretty_xml)

                self.logger.log(f"✅ Saved XML: {output_file} ({successful} entries)", "SUCCESS")
            except Exception as e:
                self.logger.log(f"❌ Error saving XML: {e}", "ERROR")
                return
        else:
            self.logger.log("⚠️  No successful entries to save", "WARNING")

        # Save failed titles
        if self.title_fixer.failed_titles:
            self.title_fixer.save_failed_titles()

        # Final summary
        self.logger.log("="*50, "INFO")
        self.logger.log(f"📊 PROCESSING COMPLETE", "INFO")
        self.logger.log(f"✅ Successful: {successful}/{final_count}", "SUCCESS")
        self.logger.log(f"❌ Failed: {failed}/{final_count}", "ERROR")
        self.logger.log(f"⏭️  Skipped: {skipped} (already processed)", "INFO")

        if failed > 0:
            self.logger.log(f"📄 Check {CONFIG['failed_titles_file']} for failed titles", "WARNING")

        self.logger.log("="*50, "INFO")
        input("\nPress Enter to continue...")

    def _create_manga_entry(self, mal_id, mal_title):
        """Create manga XML entry with validation"""
        if not mal_id or not mal_title:
            raise ValueError("MAL ID and title are required")

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
        """Create anime XML entry with validation"""
        if not mal_id or not mal_title:
            raise ValueError("MAL ID and title are required")

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
        """Display recent logs with improved formatting"""
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

        print("="*70)
        input("\nPress Enter to continue...")

    def show_progress_stats(self):
        """Show detailed progress statistics"""
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

        # Show recent failed entries
        if self.progress.data['failed_entries']:
            print("\n❌ Recent failed entries:")
            print("-" * 40)
            for entry in self.progress.data['failed_entries'][-10:]:
                print(f"• {entry['title']} - {entry['reason']}")

        # Session info
        if 'session_start' in self.progress.data:
            print(f"\n🕒 Session started: {self.progress.data['session_start']}")

        print("="*70)
        input("\nPress Enter to continue...")

    def clear_progress(self):
        """Clear progress and cache files with confirmation"""
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
        """Main program loop with comprehensive error handling"""
        try:
            self.logger.log("Enhanced Aniyomi to MAL Converter v2.0 started", "INFO")

            while True:
                try:
                    choice = self.show_menu()

                    if choice == "1":
                        self.generate_mal_ids()
                    elif choice == "2":
                        print("\nℹ️  Use fast_mal_import.py for Step 2 (Create Import Chunks)")
                        print("Example: python fast_mal_import.py manga mal_manga_import.xml mangalist.xml")
                        input("\nPress Enter to continue...")
                    elif choice == "3":
                        xml_file = self.get_file_input("Enter XML file to validate: ")
                        if xml_file:
                            while True:
                                is_anime_input = input("Is this anime? (y/n): ").lower().strip()
                                if is_anime_input in ['y', 'yes']:
                                    is_anime = True
                                    break
                                elif is_anime_input in ['n', 'no']:
                                    is_anime = False
                                    break
                                print("❌ Please enter 'y' for yes or 'n' for no")

                            self.validator.validate_mal_xml(xml_file, is_anime)
                            input("\nPress Enter to continue...")
                    elif choice == "4":
                        self.show_logs()
                    elif choice == "5":
                        self.show_progress_stats()
                    elif choice == "6":
                        self.clear_progress()
                    elif choice == "7":
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
                    print("The error has been logged. You can continue or restart the program.")
                    input("Press Enter to continue...")

        except Exception as e:
            self.logger.log(f"Critical error in main loop: {e}", "ERROR")
            self.logger.log(f"Full traceback: {traceback.format_exc()}", "ERROR")
            print(f"\n💥 Critical error: {e}")
            print("Check the log file for details.")
        finally:
            self.logger.log("Converter session ended", "INFO")

if __name__ == "__main__":
    try:
        converter = MasterConverter()
        converter.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Failed to start converter: {e}")
        print("Make sure you have installed: pip install pandas requests")
        sys.exit(1)
