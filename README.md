Bước 1 
uv init crawl-topcv-jobs

Bước 2
uv add pandas matplotlib seaborn ipykernel selenium webdriver_manager


gh auth login

gh repo create crawl-topcv-jobs --private --source=. --remote=origin --push

Bước 3 Cài chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

sudo apt install ./google-chrome-stable_current_amd64.deb