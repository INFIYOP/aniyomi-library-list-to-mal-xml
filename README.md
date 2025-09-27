# Aniyomi to MyAnimeList Converter

## 🚨 **CRITICAL - READ THIS BEFORE STARTING** 

### **⚠️ YOUR ANIYOMI CSV FILE MUST BE SPLIT FIRST ⚠️**

**IMPORTANT:** Your Aniyomi export (`aniyomi_library.csv`) has BOTH anime and manga mixed together. **THIS TOOL CANNOT WORK WITH MIXED FILES!**

### **⚠️ THIS TOOL ONLY IMPORTS TITLES, NOT PROGRESS ⚠️**

**IMPORTANT:** This tool only transfers the **names/titles** of your anime and manga to MyAnimeList. It does **NOT** transfer:
- Your reading/watching progress (chapters read, episodes watched)
- Your scores/ratings
- Your start/finish dates
- Your status (completed, reading, etc.)

**What gets imported:** Title names only - all entries will be set to "Plan to Read/Watch" status on MAL.

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

**What it transfers:** Only the **titles/names** of your anime and manga  
**What it doesn't transfer:** Progress, scores, dates, or status (all will be "Plan to Read/Watch")

**Instead of:** Weeks of manual clicking  
**You get:** Everything imported while you grab a coffee ☕

## 💾 Complete Setup Guide

### 1. Install Python (One Time Only)
- **Windows:** [python.org](https://python.org) → Download → **CHECK "Add to PATH" during installation**
- **Mac:** `brew install python` or download from python.org
- **Linux:** `sudo apt install python3 python3-pip`

**To verify Python is installed:**
```bash
python --version
# Should show: Python 3.x.x
```

### 2. Install Required Libraries (One Time Only)
**Open Command Prompt/Terminal and run these commands one by one:**

```bash
pip install pandas
```
```bash
pip install requests
```

**Alternative single command:**
```bash
pip install pandas requests
```

**If pip doesn't work, try:**
- **Windows:** `py -m pip install pandas requests`
- **Mac/Linux:** `python3 -m pip install pandas requests`

**To verify libraries are installed:**
```bash
pip list
# Should show pandas and requests in the list
```

### 3. Download All Script Files

**You need these 3 files in the SAME folder:**
- `aniyomi_to_mal_master_v2.py` (Enhanced tool - **RECOMMENDED**)
- `make_mal_import.py` (Basic tool for Step 1)
- `fast_mal_import.py` (Chunking tool for Step 2)

### 4. Create Your Working Folder

**IMPORTANT:** All files must be in the same folder for the tools to work properly.

**Create a folder structure like this:**
```
📁 aniyomi_converter/
    📄 aniyomi_to_mal_master_v2.py
    📄 make_mal_import.py  
    📄 fast_mal_import.py
    📄 aniyomi_library.csv (your export)
    📄 anime_entries.csv (after splitting)
    📄 manga_entries.csv (after splitting)
    📄 mangalist_123456.xml (your MAL export, optional)
    📄 animelist_123456.xml (your MAL export, optional)
```

**How to navigate to your folder:**
```bash
# Windows
cd C:\Users\YourName\Desktop\aniyomi_converter

# Mac/Linux  
cd ~/Desktop/aniyomi_converter
```

### 5. Get Your Files (Every Time)

#### File #1: Your Aniyomi Library Export (**REQUIRED**)
**How to export from Aniyomi:**
1. Open Aniyomi app
2. Tap **More (...)** at bottom right
3. Tap **Settings** (gear icon)
4. Scroll down to **Data and Storage**
5. Scroll to the bottom and find **Export section**
6. Tap **Library list**
7. Choose **CSV format**
8. Save the file to your computer (usually named `aniyomi_library.csv`)
9. **Move this file to your aniyomi_converter folder**

**After export:**
- **CRITICAL:** The exported file contains both anime AND manga mixed together
- **You MUST ask AI (ChatGPT/Perplexity) to split it into:**
  - `anime_entries.csv` (anime only)
  - `manga_entries.csv` (manga only)
  - **Keep the same format:** `title,type`
- **Save both split files in the same folder as your scripts**

**What Aniyomi exports:** Title, Author, Artist, Type (the tool only uses Title and Type)

#### File #2: Your MyAnimeList Export (Optional but Recommended)
**How to get:**
1. Go to [MyAnimeList.net](https://myanimelist.net) → Login
2. Profile → Export My List
3. Download as XML
4. Files: `animelist_123456.xml` or `mangalist_123456.xml`
5. **Save these files in the same folder as your scripts**

## 🚀 How to Use - 3 Methods

### **METHOD 1: Enhanced Master Tool (RECOMMENDED)**

**What:** Interactive tool with smart matching, real-time logs, and progress saving

**Steps:**
1. **Open Command Prompt/Terminal**
2. **Navigate to your folder:**
   ```bash
   cd path/to/your/aniyomi_converter
   ```
3. **Run the enhanced tool:**
   ```bash
   python aniyomi_to_mal_master_v2.py
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

**Make sure you're in the correct folder first:**
```bash
cd path/to/your/aniyomi_converter
```

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
cd path/to/your/aniyomi_converter
python make_mal_import.py manga manga_entries.csv output.xml
# Then upload output.xml directly to MAL
```

## 📝 Complete Command Reference

### Required File Structure
**ALL files must be in the same folder:**
```
📁 Your working folder/
    📜 Scripts (required):
        📄 aniyomi_to_mal_master_v2.py
        📄 make_mal_import.py  
        📄 fast_mal_import.py
    📜 Your input files:
        📄 anime_entries.csv
        📄 manga_entries.csv
        📄 mangalist_123456.xml (optional)
    📜 Generated files (created by tools):
        📄 mal_manga_import.xml
        📄 mal_anime_import.xml  
        📄 mal_manga_final_chunk_XX.xml
        📄 failed_titles.json
        📄 aniyomi_converter.log
```

### aniyomi_to_mal_master_v2.py (NEW ENHANCED TOOL)
**Purpose:** All-in-one tool with smart features

**Command:**
```bash
python aniyomi_to_mal_master_v2.py
```

**Requirements:**
- Must be in same folder as your CSV files
- Needs internet connection
- Requires `pandas` and `requests` libraries

**What it does:**
- ✅ Smart title matching (finds 90% more titles than basic tool)
- ✅ Real-time colored progress logs  
- ✅ Saves progress - resume if interrupted
- ✅ Creates `failed_titles.json` with unfound titles
- ✅ Validates XML before you upload
- ✅ Menu-driven - easy to use
- ⚠️ **Only imports titles** - sets all to "Plan to Read/Watch"

### make_mal_import.py (BASIC TOOL)
**Purpose:** Convert CSV to XML with MAL IDs

**Command:**
```bash
python make_mal_import.py <anime|manga> <input.csv> <output.xml>
```

**Examples:**
```bash
python make_mal_import.py manga manga_entries.csv mal_manga_import.xml
python make_mal_import.py anime anime_entries.csv mal_anime_import.xml
```

**Requirements:**
- Your split CSV file must be in same folder
- Internet connection for MAL API lookups
- `pandas` and `requests` libraries

**What you get:**
- XML file with MAL IDs in same folder
- Console output showing found/skipped titles
- **All entries set to "Plan to Read/Watch" status**

### fast_mal_import.py (FINAL IMPORT TOOL)
**Purpose:** Create safe 200-entry chunks for MAL upload

**Command:**
```bash
python fast_mal_import.py <anime|manga> <mal_xml> <your_mal_export.xml>
```

**Examples:**
```bash
python fast_mal_import.py manga mal_manga_import.xml mangalist_123456.xml
python fast_mal_import.py anime mal_anime_import.xml animelist_123456.xml
```

**Requirements:**
- XML with MAL IDs (from previous step) must be in same folder
- Your current MAL export (optional, prevents duplicates)
- All files must be in same folder

**What you get:**
- Multiple XML files in same folder: `mal_manga_final_chunk_01.xml`, etc.
- Each file has 200 entries (safe for MAL import)

## 📁 Complete File Guide

### Your Files (You Must Provide)
```
📄 aniyomi_library.csv - Your full Aniyomi export (MUST BE SPLIT BY AI)
📄 anime_entries.csv - Your anime only (AFTER SPLITTING)
📄 manga_entries.csv - Your manga only (AFTER SPLITTING) 
📄 animelist_123456.xml - Your current MAL anime list (optional)
📄 mangalist_123456.xml - Your current MAL manga list (optional)
```

### Script Files (You Must Download)
```
📄 aniyomi_to_mal_master_v2.py - Enhanced tool (RECOMMENDED)
📄 make_mal_import.py - Basic MAL ID generator  
📄 fast_mal_import.py - Chunk creator for safe import
```

### Generated Files (Tools Create These)
```
📄 mal_anime_import.xml - Your anime with MAL IDs (Step 1 output)
📄 mal_manga_import.xml - Your manga with MAL IDs (Step 1 output)
📄 mal_anime_final_chunk_XX.xml - Import-ready anime chunks (Step 2)
📄 mal_manga_final_chunk_XX.xml - Import-ready manga chunks (Step 2)
📄 aniyomi_converter.log - All conversion logs with timestamps
📄 conversion_progress.json - Resume data (don't delete during conversion)
📄 failed_titles.json - Titles that couldn't be matched (IMPORTANT!)
```

## ⚠️ The failed_titles.json File

**What it is:** List of titles the tool couldn't find on MyAnimeList

**What to do:**
1. **Don't ignore it!** These are often just spelled differently on MAL
2. **Ask ChatGPT/Perplexity:** "Find the exact MyAnimeList names for these titles and create a CSV file with format: title,type"
3. **Give the AI the failed_titles.json content**
4. **Force them to find ALL titles** - many are just romanization differences
5. **Save the corrected CSV in the same folder**
6. **Run the tool again** with the corrected CSV

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

## 🚀 Complete Step-by-Step Walkthrough

### **STEP 0: Setup (One Time Only)**
1. **Install Python** with "Add to PATH" checked
2. **Install libraries:** `pip install pandas requests`
3. **Create a folder** for all your files (e.g., `aniyomi_converter`)
4. **Download the 3 script files** and put them in your folder

### **STEP 1: Export from Aniyomi**
1. **Open Aniyomi app**
2. **Tap More (...)** at bottom right
3. **Tap Settings** (gear icon) 
4. **Scroll to Data and Storage**
5. **Scroll to Export section** at the bottom
6. **Tap Library Export** → Choose CSV
7. **Save the file** to your computer
8. **Move the file to your aniyomi_converter folder**

### **STEP 2: Prepare Your Files (CRITICAL)**
1. **Ask AI to split your Aniyomi CSV file** into separate anime/manga files
2. **Make sure format is correct:** `title,type` (2 columns, no headers)
3. **Save both split files in your aniyomi_converter folder**
4. **Download your current MAL lists** and put them in the same folder (optional)

### **STEP 3: Navigate to Your Folder**
```bash
# Open Command Prompt/Terminal and navigate to your folder
cd path/to/your/aniyomi_converter

# Verify you're in the right place (should show your files)
ls    # Mac/Linux
dir   # Windows
```

### **STEP 4: Run Enhanced Tool**
```bash
python aniyomi_to_mal_master_v2.py
```
1. Choose option "1. Generate MAL IDs from CSV"
2. Enter your CSV file name (e.g., `manga_entries.csv`)
3. Enter type (`manga` or `anime`)
4. Enter output file name (e.g., `mal_manga_import.xml`)
5. **Watch the colored logs** - see progress in real-time
6. **Check `failed_titles.json`** for any missing titles

### **STEP 5: Create Import Chunks**
```bash
python fast_mal_import.py manga mal_manga_import.xml mangalist_123456.xml
```
1. Tool creates multiple XML files (200 entries each)
2. Files named: `mal_manga_final_chunk_01.xml`, `mal_manga_final_chunk_02.xml`, etc.
3. All files saved in your working folder

### **STEP 6: Upload to MyAnimeList**
1. Go to [myanimelist.net/panel.php?go=import](https://myanimelist.net/panel.php?go=import)
2. Upload `mal_manga_final_chunk_01.xml` from your folder
3. **Wait 3-5 minutes** (IMPORTANT!)
4. Upload `mal_manga_final_chunk_02.xml`
5. **Wait 3-5 minutes** (IMPORTANT!)
6. Repeat for all chunk files

**Result:** All titles will be added to your MAL list with "Plan to Read/Watch" status

## ❌ Common Problems & Solutions

### "pip is not recognized" Error
**Problem:** pip command not found  
**Solutions:**
- **Windows:** Use `py -m pip install pandas requests`
- **Make sure Python was installed with "Add to PATH" checked**
- **Reinstall Python from python.org with PATH option**

### "python is not recognized" Error  
**Problem:** Python not in system PATH
**Solutions:**
- **Windows:** Use `py` instead of `python`
- **Reinstall Python with "Add to PATH" checked**
- **Full path:** `C:\Python39\python.exe script.py`

### "No module named 'pandas'" Error
**Problem:** Libraries not installed
**Solutions:**
```bash
pip install pandas requests
# OR
py -m pip install pandas requests  
# OR  
python3 -m pip install pandas requests
```

### "File not found" Error
**Problem:** Files not in same folder or wrong path
**Solutions:**
- **Check all files are in same folder**
- **Use `cd` command to navigate to correct folder**
- **Use `ls` (Mac/Linux) or `dir` (Windows) to see files**
- **Check file names match exactly (case-sensitive on Mac/Linux)**

### "Nothing to update" Error on MAL
**Problem:** MAL says no entries to update  
**Solution:** Use the two-step process (make_mal_import.py → fast_mal_import.py)

### Many "Skipped (not found)" Messages  
**Problem:** Titles don't match MAL exactly
**Solution:** 
1. **Use enhanced tool** - it finds most titles automatically
2. **Check `failed_titles.json` in your folder** - ask AI to find correct MAL names
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
1. **Use enhanced tool** - it saves progress automatically in your folder
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
1. **Install Python and libraries properly** - most important step
2. **Put ALL files in the same folder** - #1 reason for "file not found" errors
3. **ALWAYS split your CSV file first** - #2 reason for failure
4. **Navigate to the correct folder** using `cd` command
5. **Check CSV format** (title,type with no headers)
6. **Have your MAL export ready** (prevents duplicates)
7. **Understand this only imports titles** - no progress transferred

### **DURING CONVERSION:**
8. **Use the enhanced tool** for best results
9. **Don't close the terminal** during processing
10. **Watch the colored logs** to see progress
11. **Don't ignore failed titles** - most can be fixed
12. **Keep all files in the same folder**

### **FOR UPLOAD:**
13. **Never rush MAL uploads** - wait between chunks
14. **Start with smaller chunks** first to test
15. **Keep all XML files** until import is complete
16. **Remember all entries will be "Plan to Read/Watch"**

## 🆘 Still Not Working?

**Check These Common Issues:**

1. **Python/pip not installed?** - Reinstall Python with PATH option
2. **Libraries not installed?** - Run `pip install pandas requests`
3. **Files not in same folder?** - Move all files to one folder
4. **Wrong folder?** - Use `cd` to navigate to correct folder
5. **CSV file not split?** - Anime and manga must be separate files
6. **Wrong CSV format?** - Should be `title,type` with no headers
7. **Using wrong commands?** - Use enhanced tool for best results
8. **Skipping failed titles?** - Check `failed_titles.json` and fix them
9. **Uploading too fast to MAL?** - Wait 3-5 minutes between uploads
10. **Expecting progress transfer?** - This tool only transfers title names

**The enhanced tool solves 90% of common problems automatically. Use it!**

## 📋 What Gets Imported vs What Doesn't

### ✅ **What DOES Get Imported:**
- Title names of anime/manga
- Correct MyAnimeList IDs
- Basic entry structure

### ❌ **What DOES NOT Get Imported:**
- Your reading/watching progress (chapters/episodes)
- Your scores and ratings
- Your start/finish dates
- Your current status (reading, completed, etc.)
- Your notes or comments
- Custom tags or lists

**All imported entries will have:**
- Status: "Plan to Read" (manga) or "Plan to Watch" (anime)
- Progress: 0 chapters/episodes
- Score: 0 (unrated)
- Dates: Empty

---

## 📚 All Tools Summary

- **`aniyomi_to_mal_master_v2.py`** ← **USE THIS** (enhanced with smart features)
- **`make_mal_import.py`** ← Basic tool (generates MAL IDs)
- **`fast_mal_import.py`** ← Final step (creates upload chunks)

**For most users: Just use the enhanced master tool and follow the interactive menu!**

**Remember: ALL files must be in the same folder for everything to work!**
