import os
import glob

def cleanup_files():
  directory = '/Users/claireli/_abc/_pr/static/graph_images'
  png_files = glob.glob(os.path.join(directory, '*.png'))
  png_files.sort(key=os.path.getmtime, reverse=True)

  # Keep only the 20 newest files
  files_to_keep = png_files[:20]

  for file in png_files:
    if file not in files_to_keep:
      os.remove(file)
      print(f'Deleted: {file}')

  print("Cleanup complete.")
