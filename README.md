# Aniyomi to MyAnimeList Converter

## 🚨 **CRITICAL - READ THIS BEFORE STARTING** 

### **⚠️ YOUR ANIYOMI CSV FILE MUST BE SPLIT FIRST ⚠️**

**IMPORTANT:** Your Aniyomi export (`aniyomi_library.csv`) has BOTH anime and manga mixed together. **THIS TOOL CANNOT WORK WITH MIXED FILES!**

**YOU MUST DO THIS:**
1. **Ask ChatGPT or Perplexity:** "Split this CSV file into anime_entries.csv (anime only) and manga_entries.csv (manga only). Keep the same format with 2 columns: title,type"
2. **For titles that exist as BOTH anime and manga** (like "Attack on Titan"), **put the same title in BOTH CSV files**
3. **DO NOT change the format** - keep exactly 2 columns: `title,type`

**WHEN TITLES ARE "SKIPPED (NOT FOUND)":**
- The tool will show titles it couldn't find on MyAnimeList
- **DON'T IGNORE THESE!** Copy all skipped titles
- **Ask AI:** "Find the exact MyAnimeList names for these titles and make a CSV with format: title,type"
- **Force the AI to find ALL titles** - don't accept "some couldn't be found"
- The new enhanced tool will try to fix most of these automatically

---

## 🎯 What This Tool Does

**Problem:** You have 1000+ anime/manga in Aniyomi and want them on MyAnimeList  
**Solution:** This tool moves them all automatically in 30 minutes

**Instead of:** Weeks of manual clicking  
**You get:** Everything imported while you grab a coffee ☕

## 💾 What You Need

### 1. Install Python (One Time Only)
- **Windows:** [python.org](https://python.org) → Download → **CHECK "Add to PATH"**
- **Mac:** `brew install python` or download from python.org
- **Linux:** `sudo apt install python3 python3-pip`

### 2. Install Libraries (One Time Only) 
```bash
pip install pandas requests
```

### 3. Get Your Files (Every Time)

#### File #1: Your Split Aniyomi Files (**REQUIRED**)
**How to get:**
1. Aniyomi → Settings → Data and Storage → Create Backup
2. Choose "Library entries only" + CSV format  
3. **CRITICAL:** Ask AI to split into:
   - `anime_entries.csv` (anime only)
   - `manga_entries.csv` (manga only)
   - **Same format:** `title,type`

#### File #2: Your MyAnimeList Export (Optional)
**How to get:**
1. [MyAnimeList.net](https://myanimelist.net) → Profile → Export My List
2. Download as XML
3. Files: `animelist_123456.xml` or `mangalist_123456.xml`

## 🚀 How to Use - 3 Methods

### **METHOD 1: Enhanced Master Tool (RECOMMENDED)**

**What:** Interactive tool with smart matching, real-time logs, and progress saving

```bash
python aniyomi_to_mal_master.py
```

**Features:**
- 🎨 **Real-time colored logs** (blue/green/yellow/red)
- 💾 **Never lose progress** - resume from interruptions
- 🧠 **Smart title matching** - finds titles even with typos/different names
- 📁 **Auto-saves failed titles** to `failed_titles.json` for manual review
- ✅ **XML validation** before import
- 📋 **Interactive menu** - no need to remember commands

**Menu Options:**
```
1. Generate MAL IDs from CSV (Step 1)
2. Create Import Chunks (Step 2) 
3. Validate XML Files
4. Show Conversion Logs
5. Resume Previous Session
6. Clear Progress/Cache
7. Exit
```

### **METHOD 2: Two-Step Process (For Large Libraries)**

**Step 1: Generate MAL IDs**
```bash
python make_mal_import.py manga manga_entries.csv mal_manga_import.xml
python make_mal_import.py anime anime_entries.csv mal_anime_import.xml
```

**Step 2: Create Safe Import Chunks**
```bash
python fast_mal_import.py manga mal_manga_import.xml mangalist_123456.xml
python fast_mal_import.py anime mal_anime_import.xml animelist_123456.xml
```

### **METHOD 3: Quick Single-Step (Small Libraries Only)**

```bash
python make_mal_import.py manga manga_entries.csv output.xml
# Then upload output.xml directly to MAL
```

## 📝 Complete Command Guide

### aniyomi_to_mal_master.py (NEW ENHANCED TOOL)
**Purpose:** All-in-one tool with smart features

```bash
python aniyomi_to_mal_master.py
# Interactive menu will guide you
```

**What it does:**
- ✅ Smart title matching (finds 90% more titles than basic tool)
- ✅ Real-time colored progress logs  
- ✅ Saves progress - resume if interrupted
- ✅ Creates `failed_titles.json` with unfound titles
- ✅ Validates XML before you upload
- ✅ Menu-driven - easy to use

### make_mal_import.py (BASIC TOOL)
**Purpose:** Convert CSV to XML with MAL IDs

```bash
python make_mal_import.py <anime|manga> <input.csv> <output.xml>
```

**Examples:**
```bash
python make_mal_import.py manga manga_entries.csv mal_manga_import.xml
python make_mal_import.py anime anime_entries.csv mal_anime_import.xml
```

**You need:**
- Your split CSV file (`anime_entries.csv` or `manga_entries.csv`)
- Internet connection (to lookup MAL IDs)

**You get:**
- XML file with MAL IDs
- Console output showing found/skipped titles

### fast_mal_import.py (FINAL IMPORT TOOL)
**Purpose:** Create safe 200-entry chunks for MAL upload

```bash
python fast_mal_import.py <anime|manga> <mal_xml> <your_mal_export.xml>
```

**Examples:**
```bash
python fast_mal_import.py manga mal_manga_import.xml mangalist_123456.xml
python fast_mal_import.py anime mal_anime_import.xml animelist_123456.xml
```

**You need:**
- XML with MAL IDs (from previous step)
- Your current MAL export (optional, prevents duplicates)

**You get:**
- Multiple XML files: `mal_manga_final_chunk_01.xml`, `mal_manga_final_chunk_02.xml`, etc.
- Each file has 200 entries (safe for MAL import)

## 📁 File Guide - What Each File Does

### Your Files (You Provide)
- `anime_entries.csv` - Your anime from Aniyomi (**MUST BE SPLIT FROM MAIN FILE**)
- `manga_entries.csv` - Your manga from Aniyomi (**MUST BE SPLIT FROM MAIN FILE**)
- `animelist_123456.xml` - Your current MAL anime list (optional)
- `mangalist_123456.xml` - Your current MAL manga list (optional)

### Generated Files (Tool Creates)
- `mal_anime_import.xml` - Your anime with MAL IDs (Step 1 output)
- `mal_manga_import.xml` - Your manga with MAL IDs (Step 1 output)
- `mal_anime_final_chunk_XX.xml` - Ready-to-import anime chunks (Step 2 output)
- `mal_manga_final_chunk_XX.xml` - Ready-to-import manga chunks (Step 2 output)

### Enhanced Tool Files (Master Tool Creates)
- `aniyomi_converter.log` - All conversion logs with timestamps
- `conversion_progress.json` - Resume data (don't delete during conversion)
- `failed_titles.json` - Titles that couldn't be matched (**IMPORTANT!**)

## ⚠️ The failed_titles.json File

**What it is:** List of titles the tool couldn't find on MyAnimeList

**What to do:**
1. **Don't ignore it!** These are often just spelled differently on MAL
2. **Ask ChatGPT/Perplexity:** "Find the exact MyAnimeList names for these titles and create a CSV file with format: title,type"
3. **Give the AI the failed_titles.json content**
4. **Force them to find ALL titles** - many are just romanization differences
5. **Run the tool again** with the corrected CSV

## 🎨 What the Enhanced Logs Look Like

```
[2025-09-28 00:04:15] [INFO] Starting MAL ID generation for manga
[2025-09-28 00:04:16] [INFO] Processing (1/2914): Attack on Titan  
[2025-09-28 00:04:17] [SUCCESS] ✓ Added: Attack on Titan → Shingeki no Kyojin (ID: 23390)
[2025-09-28 00:04:18] [WARNING] Fuzzy match: One Piece → One Piece (ID: 13)
[2025-09-28 00:04:19] [ERROR] ✗ Failed: Some Random Title
```

**Colors:**
- 🔵 **Blue** = Information
- 🟢 **Green** = Success (found title)  
- 🟡 **Yellow** = Warning (fuzzy match)
- 🔴 **Red** = Error (title not found)

## 🚀 Step-by-Step Walkthrough

### **STEP 0: Prepare Your Files (CRITICAL)**
1. **Split your Aniyomi CSV file** - Ask AI to do this
2. **Make sure format is correct:** `title,type` (2 columns, no headers)
3. **Download your current MAL lists** (optional but recommended)

### **STEP 1: Run Enhanced Tool**
```bash
python aniyomi_to_mal_master.py
```
1. Choose option "1. Generate MAL IDs from CSV"
2. Enter your CSV file path (e.g., `manga_entries.csv`)
3. Enter type (`manga` or `anime`)
4. Enter output file name (e.g., `mal_manga_import.xml`)
5. **Watch the colored logs** - see progress in real-time
6. **Check `failed_titles.json`** for any missing titles

### **STEP 2: Create Import Chunks**
```bash
python fast_mal_import.py manga mal_manga_import.xml mangalist_123456.xml
```
1. Tool creates multiple XML files (200 entries each)
2. Files named: `mal_manga_final_chunk_01.xml`, `mal_manga_final_chunk_02.xml`, etc.

### **STEP 3: Upload to MyAnimeList**
1. Go to [myanimelist.net/panel.php?go=import](https://myanimelist.net/panel.php?go=import)
2. Upload `mal_manga_final_chunk_01.xml`  
3. **Wait 3-5 minutes** (IMPORTANT!)
4. Upload `mal_manga_final_chunk_02.xml`
5. **Wait 3-5 minutes** (IMPORTANT!)
6. Repeat for all chunks

## ❌ Common Problems & Solutions

### "Nothing to update" Error on MAL
**Problem:** MAL says no entries to update  
**Solution:** Use the two-step process (make_mal_import.py → fast_mal_import.py)

### Many "Skipped (not found)" Messages  
**Problem:** Titles don't match MAL exactly
**Solution:** 
1. **Use enhanced tool** - it finds most titles automatically
2. **Check `failed_titles.json`** - ask AI to find correct MAL names
3. **Japanese titles** often need romanization (e.g., "Shingeki no Kyojin" vs "Attack on Titan")

### CSV Format Errors
**Problem:** Tool can't read your CSV  
**Solution:** Make sure format is exactly:
```
Attack on Titan,anime
One Piece,manga
Naruto,manga
```
- No headers
- Exactly 2 columns
- Comma separated
- No extra text

### File Too Large Error
**Problem:** MAL won't accept your XML file  
**Solution:** Always use `fast_mal_import.py` - it splits into 200-entry chunks

### Progress Lost Due to Interruption  
**Problem:** Tool stopped and you lost progress
**Solution:** 
1. **Use enhanced tool** - it saves progress automatically
2. **Choose option 5** to resume from where you left off
3. **Never delete `conversion_progress.json`** during conversion

## ⏱️ How Long This Takes

| Library Size | Enhanced Tool | Basic Tool | Upload Time |
|-------------|---------------|------------|-------------|
| 100 entries | 2-3 minutes | 5-8 minutes | 5 minutes |
| 500 entries | 8-12 minutes | 15-20 minutes | 15 minutes |
| 1000+ entries | 15-25 minutes | 30-45 minutes | 30+ minutes |
| 2000+ entries | 25-40 minutes | 60-90 minutes | 60+ minutes |

**Enhanced tool is faster because:**
- ✅ Smart caching and resume
- ✅ Better title matching (fewer retries)
- ✅ Optimized API usage

## 🎉 Success Tips

### **BEFORE YOU START:**
1. **ALWAYS split your CSV file first** (#1 reason for failure)
2. **Check CSV format** (title,type with no headers)
3. **Have your MAL export ready** (prevents duplicates)

### **DURING CONVERSION:**
4. **Use the enhanced tool** for best results
5. **Don't close the terminal** during processing
6. **Watch the colored logs** to see progress
7. **Don't ignore failed titles** - most can be fixed

### **FOR UPLOAD:**
8. **Never rush MAL uploads** - wait between chunks
9. **Start with smaller chunks** first to test
10. **Keep all XML files** until import is complete

## 🆘 Still Not Working?

**Check These Common Issues:**

1. **CSV file not split?** - Anime and manga must be separate files
2. **Wrong CSV format?** - Should be `title,type` with no headers
3. **Using wrong commands?** - Use enhanced tool for best results
4. **Skipping failed titles?** - Check `failed_titles.json` and fix them
5. **Uploading too fast to MAL?** - Wait 3-5 minutes between uploads

**The enhanced tool solves 90% of common problems automatically. Use it!**

---

## 📚 All Tools Summary

- **`aniyomi_to_mal_master.py`** ← **USE THIS** (enhanced with smart features)
- **`make_mal_import.py`** ← Basic tool (generates MAL IDs)
- **`fast_mal_import.py`** ← Final step (creates upload chunks)

**For most users: Just use the enhanced master tool and follow the interactive menu!**
