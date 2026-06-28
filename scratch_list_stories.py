import os

def main():
    stories_dir = 'docs/stories'
    if not os.path.exists(stories_dir):
        print(f"Directory {stories_dir} does not exist.")
        return
        
    for root, dirs, files in os.walk(stories_dir):
        print(f"\nDirectory: {root}")
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                print(f"  - {file} ({os.path.getsize(path)} bytes)")

if __name__ == '__main__':
    main()
