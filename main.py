import subprocess
import os
import time

# -------- CONFIG --------
ROOT_DOWNLOAD_DIR = "attention_videos"
YTDLP_BIN = "yt-dlp"  # change if yt-dlp is not in PATH
# ------------------------

# Create root directory
os.makedirs(ROOT_DOWNLOAD_DIR, exist_ok=True)

attention_roadmap = {
    "basic_standard_attention": [
        {
            "title": "Attention Is All You Need – Explanation",
            "url": "https://www.youtube.com/watch?v=w76Dpp7b3B4"
        }
    ],

    "self_attention": [
        {
            "title": "Attention in Transformers",
            "url": "https://www.youtube.com/watch?v=N7WyaOuhBHQ"
        }
    ],

    "multi_head_attention": [
        {
            "title": "Transformer – Understanding Multi-Head Attention",
            "url": "https://www.youtube.com/watch?v=2BRAU7nGTAw"
        },
        {
            "title": "Multi-Head Latent Attention Coded from Scratch in Python",
            "url": "https://www.youtube.com/watch?v=mIaWmJVrMpc"
        }
    ],

    "cross_attention": [
        {
            "title": "Intro to Attention and Its Forms",
            "url": "https://www.youtube.com/watch?v=IR8PqmGTGyw"
        }
    ],

    "sparse_efficient_attention": [
        {
            "title": "Intro to Attention and Its Forms",
            "url": "https://www.youtube.com/watch?v=IR8PqmGTGyw"
        },
        {
            "title": "Hardware Efficient Attention for Fast Decoding",
            "url": "https://www.youtube.com/watch?v=oHkMoQi8Z7M"
        }
    ],

    "linear_attention": [
        {
            "title": "Intro to Attention and Its Forms",
            "url": "https://www.youtube.com/watch?v=IR8PqmGTGyw"
        }
    ],

    "performer_kernelized_attention": [
        {
            "title": "Intro to Attention and Its Forms",
            "url": "https://www.youtube.com/watch?v=IR8PqmGTGyw"
        }
    ],

    "memory_persistent_attention": [
        {
            "title": "ATLAS: Learning to Optimally Memorize the Context at Test Time",
            "url": "https://www.youtube.com/watch?v=cNfX1aRr9Hg"
        }
    ],

    "relative_positional_attention": [
        {
            "title": "Attention Is All You Need – Explanation",
            "url": "https://www.youtube.com/watch?v=w76Dpp7b3B4"
        }
    ],

    "global_local_hierarchical_attention": [
        {
            "title": "Hierarchical Reasoning / Attention Models",
            "url": "https://www.youtube.com/@gabrielmongaras/videos"
        }
    ],

    "attention_with_recurrence_feedback": [
        {
            "title": "Learning to (Learn at Test Time): RNNs with Expressive Hidden States",
            "url": "https://www.youtube.com/watch?v=I9Ghw2Z7Gqk"
        }
    ],

    "adaptive_dynamic_attention": [
        {
            "title": "From Sparse to Soft Mixtures of Experts Explained",
            "url": "https://www.youtube.com/watch?v=-IBJ1CRO9Zw"
        }
    ],

    "sparsemax_entmax_attention": [
        {
            "title": "From Sparse to Soft Mixtures of Experts Explained",
            "url": "https://www.youtube.com/watch?v=-IBJ1CRO9Zw"
        }
    ],

    "mixture_of_experts_attention": [
        {
            "title": "From Sparse to Soft Mixtures of Experts Explained",
            "url": "https://www.youtube.com/watch?v=-IBJ1CRO9Zw"
        }
    ]
}


def download_video(url: str, output_dir: str, index: int, max_retries: int = 2):
    """
    Downloads a YouTube video using yt-dlp with retry logic
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    output_template = os.path.join(
        output_dir,
        f"{index:02d} - %(title)s.%(ext)s"
    )
    
    # Try multiple download strategies
    download_strategies = [
        # Strategy 1: Best quality with subtitles (English only)
        [
            YTDLP_BIN,
            url,
            "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "--merge-output-format", "mp4",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", "en",  # English only to avoid 429 errors
            "--convert-subs", "srt",
            "--embed-subs",  # Embed subtitles in video
            "--no-write-subs",
            "-o", output_template,
            "--restrict-filenames",
            "--no-playlist",
            "--throttled-rate", "100K",  # Slow down to avoid rate limiting
            "--retries", "10",
            "--fragment-retries", "10",
            "--skip-unavailable-fragments",
            "--extractor-retries", "3"
        ],
        
        # Strategy 2: Simpler format if first fails
        [
            YTDLP_BIN,
            url,
            "-f", "best",
            "--merge-output-format", "mp4",
            "--write-subs",
            "--sub-langs", "en",
            "--convert-subs", "srt",
            "-o", output_template,
            "--restrict-filenames",
            "--no-playlist",
            "--retries", "10"
        ],
        
        # Strategy 3: Minimal download
        [
            YTDLP_BIN,
            url,
            "-f", "mp4",
            "-o", output_template,
            "--restrict-filenames",
            "--no-playlist"
        ]
    ]
    
    print(f"\nDownloading [{index:02d}] {url}")
    
    for attempt in range(max_retries + 1):
        for strategy_idx, cmd in enumerate(download_strategies):
            try:
                print(f"Attempt {attempt + 1}, Strategy {strategy_idx + 1}...")
                
                # Add delay between attempts to avoid rate limiting
                if attempt > 0 or strategy_idx > 0:
                    delay = 5 * (attempt + 1)
                    print(f"Waiting {delay} seconds before next attempt...")
                    time.sleep(delay)
                
                # Run download command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    print(f"✓ Successfully downloaded [{index:02d}]")
                    
                    # Try to download Arabic subtitles separately if English succeeded
                    if strategy_idx == 0:
                        try_download_arabic_subtitles(url, output_dir, index)
                    
                    return True
                else:
                    print(f"✗ Strategy {strategy_idx + 1} failed")
                    if "HTTP Error 429" in result.stderr:
                        print("Rate limited. Waiting longer...")
                        time.sleep(30)
                    
            except subprocess.TimeoutExpired:
                print(f"✗ Timeout for strategy {strategy_idx + 1}")
            except Exception as e:
                print(f"✗ Error with strategy {strategy_idx + 1}: {str(e)}")
    
    print(f"⚠ Failed to download after all attempts: {url}")
    return False


def try_download_arabic_subtitles(url: str, output_dir: str, index: int):
    """Try to download Arabic subtitles separately after main download"""
    try:
        print("Attempting to download Arabic subtitles separately...")
        
        # Get the video title for the filename
        get_title_cmd = [
            YTDLP_BIN,
            url,
            "--get-title",
            "--restrict-filenames",
            "--no-playlist"
        ]
        
        result = subprocess.run(
            get_title_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            title = result.stdout.strip().replace('\n', '')
            base_filename = f"{index:02d} - {title}"
            
            # Download only Arabic subtitles
            subtitle_cmd = [
                YTDLP_BIN,
                url,
                "--skip-download",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs", "ar",
                "--convert-subs", "srt",
                "-o", os.path.join(output_dir, f"{base_filename}.%(ext)s"),
                "--restrict-filenames",
                "--no-playlist",
                "--sleep-requests", "2",  # Slow down requests
                "--sleep-interval", "5"   # Sleep between requests
            ]
            
            subprocess.run(
                subtitle_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            print("✓ Arabic subtitle download attempted")
            
    except Exception as e:
        print(f"⚠ Could not download Arabic subtitles: {str(e)}")
        print("English subtitles should still be available")


def main():
    idx = 1
    successful_downloads = 0
    failed_downloads = []
    
    print("Starting YouTube downloader for Attention Mechanism videos")
    print("=" * 60)
    
    for category, videos in attention_roadmap.items():
        print(f"\n📁 Category: {category.replace('_', ' ').title()}")
        print("-" * 40)
        
        category_dir = os.path.join(ROOT_DOWNLOAD_DIR, category)
        
        for video in videos:
            title = video["title"]
            url = video["url"]
            
            print(f"\nProcessing: {title}")
            print(f"URL: {url}")
            
            success = download_video(
                url=url,
                output_dir=category_dir,
                index=idx
            )
            
            if success:
                successful_downloads += 1
            else:
                failed_downloads.append({
                    "index": idx,
                    "title": title,
                    "url": url,
                    "category": category
                })
            
            idx += 1
            
            # Add delay between videos to avoid rate limiting
            if idx < len(attention_roadmap):
                print("\nPausing for 10 seconds before next video...")
                time.sleep(10)
    
    # Summary
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✓ Successful downloads: {successful_downloads}")
    print(f"✗ Failed downloads: {len(failed_downloads)}")
    
    if failed_downloads:
        print("\nFailed videos:")
        for failed in failed_downloads:
            print(f"  {failed['index']:02d}. {failed['title']}")
            print(f"     Category: {failed['category']}")
            print(f"     URL: {failed['url']}")
    
    print(f"\n📁 All videos are saved in: {os.path.abspath(ROOT_DOWNLOAD_DIR)}")
    print("\nNote: Videos include English subtitles (embedded in video).")
    print("Arabic subtitles were attempted separately if available.")
    print("=" * 60)


if __name__ == "__main__":
    main()