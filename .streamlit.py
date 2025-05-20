import os

os.makedirs('.streamlit', exist_ok=True)
with open('.streamlit/config.toml', 'w') as f:
    f.write('')
    os.system('notepad .streamlit/config.toml')
    if os.name != 'nt':
        os.chmod('.streamlit/config.toml', 0o644)
        os.system('ls -l .streamlit/config.toml')
        print("On non-Windows: Please copy kyra_icon.png into the project folder using your file manager.")
        print("Verifying kyra_icon.png is in the project folder...")
        if os.path.isfile('kyra_icon.png'):
            print("kyra_icon.png found in the project folder.")
        else:
            print("kyra_icon.png NOT found in the project folder.")
        os.system('ls -l kyra_icon.png')
    else:
        print("On Windows: Drag and drop kyra_icon.png into the project folder using File Explorer.")
        print("Verifying kyra_icon.png is in the project folder...")
        if os.path.isfile('kyra_icon.png'):
            print("kyra_icon.png found in the project folder.")
        else:
            print("kyra_icon.png NOT found in the project folder.")
        os.system('dir kyra_icon.png')