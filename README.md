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
- The enhanced tool will try to fix most of these automatically

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

### 3. Download the Script File

**You need ONLY 1 file:**
- `aniyomi_to_mal_converter.py` (All-in-One Tool - **Everything built-in!**)

**No more multiple files needed!** Everything is in one script.

### 4. Create Your Working Folder

**IMPORTANT:** All files must be in the same folder for the tool to work properly.

**Create a folder structure like this:**
```
📁 aniyomi_converter/
    📄 aniyomi_to_mal_converter.py (THE ONLY SCRIPT YOU NEED)
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
6. Tap **Library Export**
7. Choose **CSV format**
8. Save the file to your computer (usually named `aniyomi_library.csv`)
9. **Move this file to your aniyomi_converter folder**

**After export:**
- **CRITICAL:** The exported file contains both anime AND manga mixed together
- **You MUST ask AI (ChatGPT/Perplexity) to split it into:**
  - `anime_entries.csv` (anime only)
  - `manga_entries.csv` (manga only)
  - **Keep the same format:** `title,type`
- **Save both split files in the same folder as your script**

**What Aniyomi exports:** Title, Author, Artist, Type (the tool only uses Title and Type)

#### File #2: Your MyAnimeList Export (Optional but Recommended)
**How to get:**
1. Go to [MyAnimeList.net](https://myanimelist.net) → Login
2. Profile → Export My List
3. Download as XML
4. Files: `animelist_123456.xml` or `mangalist_123456.xml`
5. **Save these files in the same folder as your script**

**⚠️ Do I need a demo XML file from MAL?**
**No!** You don't need any demo or template files. The tool creates everything from scratch. Your existing MAL export is only used to avoid duplicates (optional).

## 🚀 How to Use - All-in-One Tool

### **SINGLE SCRIPT METHOD (RECOMMENDED)**

**What:** One complete tool with everything built-in - no separate files needed!

**Steps:**
1. **Open Command Prompt/Terminal**
2. **Navigate to your folder:**
   ```bash
   cd path/to/your/aniyomi_converter
   ```
3. **Run the all-in-one tool:**
   ```bash
   python aniyomi_to_mal_converter.py
   ```

**Menu Options:**
```
🚀 ANIYOMI TO MAL CONVERTER - All-in-One Edition
============================================================
1. Generate MAL IDs from CSV (Step 1)
2. Create Import Chunks from XML (Step 2) 
3. Full Process (Steps 1 + 2 combined)     ← RECOMMENDED!
4. Validate XML Files
5. Show Conversion Logs
6. Show Progress Statistics
7. Clear Progress/Cache
8. Exit
```

### **Three Ways to Use:**

#### **Option 1: Step-by-Step**
1. Choose **"1. Generate MAL IDs from CSV"** first
2. Then choose **"2. Create Import Chunks from XML"**

#### **Option 2: Full Process (EASIEST)**
1. Choose **"3. Full Process"** - does everything automatically!

#### **Option 3: Advanced Users**
1. Use individual steps for more control

## 📝 Complete Command Reference

### aniyomi_to_mal_converter.py (ALL-IN-ONE TOOL)
**Purpose:** Complete converter with everything built-in

**Command:**
```bash
python aniyomi_to_mal_converter.py
```

**Requirements:**
- Must be in same folder as your CSV files
- Needs internet connection
- Requires `pandas` and `requests` libraries

**What it does:**
- ✅ **Step 1:** Generate MAL IDs from your CSV
- ✅ **Step 2:** Create safe 200-entry chunks for MAL upload
- ✅ **Option 3:** Do both steps automatically
- ✅ Smart title matching (finds 90% more titles than basic tools)
- ✅ Real-time colored progress logs  
- ✅ Saves progress - resume if interrupted
- ✅ Creates `failed_titles.json` with unfound titles
- ✅ Built-in XML chunking (no separate script needed)
- ✅ Menu-driven - easy to use
- ⚠️ **Only imports titles** - sets all to "Plan to Read/Watch"

## 📁 Complete File Guide

### Your Files (You Must Provide)
```
📄 aniyomi_library.csv - Your full Aniyomi export (MUST BE SPLIT BY AI)
📄 anime_entries.csv - Your anime only (AFTER SPLITTING)
📄 manga_entries.csv - Your manga only (AFTER SPLITTING) 
📄 animelist_123456.xml - Your current MAL anime list (optional)
📄 mangalist_123456.xml - Your current MAL manga list (optional)
```

### Script File (You Must Download)
```
📄 aniyomi_to_mal_converter.py - All-in-One tool (ONLY FILE YOU NEED!)
```

### Generated Files (Tool Creates These)
```
📄 mal_anime_final_chunk_XX.xml - Import-ready anime chunks
📄 mal_manga_final_chunk_XX.xml - Import-ready manga chunks  
📄 aniyomi_converter.log - All conversion logs with timestamps
📄 conversion_progress.json - Resume data (don't delete during conversion)
📄 failed_titles.json - Titles that couldn't be matched (IMPORTANT!)
```

## 🚀 Complete Step-by-Step Walkthrough

### **STEP 0: Setup (One Time Only)**
1. **Install Python** with "Add to PATH" checked
2. **Install libraries:** `pip install pandas requests`
3. **Create a folder** for all your files (e.g., `aniyomi_converter`)
4. **Download the script file** and put it in your folder

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

### **STEP 4: Run the Tool**
```bash
python aniyomi_to_mal_converter.py
```

### **STEP 5: Choose Your Method**

#### **METHOD A: Full Process (EASIEST)**
1. Choose option **"3. Full Process"**
2. Enter your CSV file name (e.g., `manga_entries.csv`)
3. Enter type (`manga` or `anime`)
4. Enter your existing MAL export (optional)
5. **Watch it do everything automatically!**

#### **METHOD B: Step-by-Step**
1. Choose option **"1. Generate MAL IDs from CSV"**
   - Enter your CSV file name
   - Enter type and output filename
   - **Watch the colored logs** - see progress in real-time
2. Choose option **"2. Create Import Chunks from XML"**
   - Enter the XML file from Step 1
   - Enter your existing MAL export (optional)
   - **Get ready-to-upload chunk files**

### **STEP 6: Upload to MyAnimeList**
1. Go to [myanimelist.net/panel.php?go=import](https://myanimelist.net/panel.php?go=import)
2. Upload `mal_manga_final_chunk_01.xml` from your folder
3. **Wait 3-5 minutes** (IMPORTANT!)
4. Upload `mal_manga_final_chunk_02.xml`
5. **Wait 3-5 minutes** (IMPORTANT!)
6. Repeat for all chunk files

**Result:** All titles will be added to your MAL list with "Plan to Read/Watch" status

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
- **Full path:** `C:\Python39\python.exe aniyomi_to_mal_converter.py`

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

### Many "Skipped (not found)" Messages  
**Problem:** Titles don't match MAL exactly
**Solution:** 
1. **Tool finds most titles automatically with smart matching**
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

### Progress Lost Due to Interruption  
**Problem:** Tool stopped and you lost progress
**Solution:** 
1. **Tool saves progress automatically in your folder**
2. **Choose option 6** to see progress statistics
3. **Restart and continue where you left off**
4. **Never delete `conversion_progress.json`** during conversion

## ⏱️ How Long This Takes

| Library Size | Generate IDs | Create Chunks | Upload Time |
|-------------|---------------|-------------|-------------|
| 100 entries | 2-3 minutes | 30 seconds | 5 minutes |
| 500 entries | 8-12 minutes | 1 minute | 15 minutes |
| 1000+ entries | 15-25 minutes | 2 minutes | 30+ minutes |
| 2000+ entries | 25-40 minutes | 3 minutes | 60+ minutes |

**All-in-one tool is faster because:**
- ✅ Smart caching and resume
- ✅ Better title matching (fewer retries)
- ✅ Optimized processing
- ✅ No file switching between steps

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
8. **Use Option 3 (Full Process) for easiest experience**
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
7. **Skipping failed titles?** - Check `failed_titles.json` and fix them
8. **Uploading too fast to MAL?** - Wait 3-5 minutes between uploads
9. **Expecting progress transfer?** - This tool only transfers title names

**The all-in-one tool solves 90% of common problems automatically. Use it!**

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

## 📚 Tool Summary

- **`aniyomi_to_mal_converter.py`** ← **THE ONLY FILE YOU NEED** (everything built-in!)

**No more multiple files! Everything is in one easy-to-use script with an interactive menu!**

**Remember: ALL files must be in the same folder for everything to work!**
