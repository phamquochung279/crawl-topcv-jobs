# CRAWL TOPCV JOBS (Learning Purposes)

Crawler nhẹ nhàng để thu thập tin tuyển dụng **Data Analyst** trên TopCV, tự động ghép **chi tiết job** + **thông tin công ty** vào một **Pandas DataFrame**, xuất **CSV/XLSX**.

## ✅ Tính năng

* Crawl từ trang search (đa trang).
* Vào từng `job_url` lấy: mức lương, địa điểm, kinh nghiệm, deadline, mô tả/yêu cầu/quyền lợi, tag, địa chỉ & thời gian làm việc.
* Vào `company_url` (nếu có) lấy: tên, website, quy mô, lĩnh vực, địa chỉ, mô tả.
* Chống **429 Too Many Requests** bằng delay ngẫu nhiên (nhẹ nhàng).
* Xuất **CSV** (và dễ mở rộng sang XLSX).

---

## 🧱 Cấu trúc project

```
.
├── airflow
│   ├── dags
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
├── scripts
│   ├── scrape_topcv_company.py # Script chính
│   └── topcv.ipynb # Notebook thử nghiệm
├── data-files
│   ├── topcv_data_analyst_jobs.csv  # Kết quả CSV (ví dụ)
│   └── topcv_data_analyst_jobs.xlsx # Kết quả XLSX (tuỳ chọn)
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## 🛠️ Yêu cầu

* Python 3.8+
* [uv](https://github.com/astral-sh/uv) (quản lý môi trường & dependency)
* (Tuỳ chọn) Google Chrome + ChromeDriver nếu bạn dùng Selenium thay vì `requests`/`BeautifulSoup`.

---

## 🚀 Bắt đầu

### Bước 1 — Khởi tạo dự án với **uv**

```bash
uv init crawl-topcv-jobs
cd crawl-topcv-jobs
```

### Bước 2 — Cài thư viện

> Script chính dùng `requests`, `beautifulsoup4`, `lxml`, `pandas`.
> Bạn có thể cài thêm các lib phục vụ phân tích (matplotlib, seaborn) hoặc Selenium nếu cần.

```bash
# Core crawl + phân tích
uv add requests beautifulsoup4 lxml pandas

# Tuỳ chọn (phân tích/plot, notebook, selenium)
uv add matplotlib seaborn ipykernel selenium webdriver-manager
```

### (Tuỳ chọn) Đẩy code lên GitHub

```bash
gh auth login
gh repo create crawl-topcv-jobs --private --source=. --remote=origin --push
```

### Bước 3 — (Tuỳ chọn) Cài Chrome cho Selenium

> Không bắt buộc nếu bạn chỉ dùng `requests` + `BeautifulSoup`.

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

---

## ▶️ Chạy crawler

Script mặc định crawl trang:

```
https://www.topcv.vn/tim-viec-lam-data-analyst?type_keyword=1&page={page}&sba=1
```

Chạy:

```bash
cd scripts
uv run scrape_topcv_company.py
```

Kết quả:

* In ra `head()` của DataFrame
* Lưu `topcv_data_analyst_jobs.csv` (UTF-8-SIG) trong thư mục hiện tại.

> Muốn đổi số trang, sửa nhanh trong `__main__`:

```python
qtpl = "https://www.topcv.vn/tim-viec-lam-data-analyst?type_keyword=1&page={page}&sba=1"
df = crawl_to_dataframe(qtpl, start_page=1, end_page=10, delay_between_pages=(0.5, 1.0))
```

---

## ⚙️ Điều chỉnh tốc độ (để tránh 429)

Script có hai “điểm nghỉ”:

* `smart_sleep(0.5, 1.0)` → nghỉ ngẫu nhiên **0.5–1.0s** giữa các request (job/company).
* `delay_between_pages=(0.5, 1.0)` → nghỉ **0.5–1.0s** giữa các **trang search**.

> Nếu vẫn bị 429:

* Tăng delay (ví dụ `smart_sleep(0.5, 1.0)`, `delay_between_pages=(0.5, 1.0)`).
* Thu hẹp số trang; chạy ngoài giờ cao điểm; dùng IP/proxy hợp lệ.
* Tái sử dụng `requests.Session()` (đã làm sẵn) để giữ cookie.
* Tôn trọng robots & điều khoản website.

---

## 🧪 Mẫu sử dụng DataFrame

Mở rộng trong notebook hoặc script khác:

```python
import pandas as pd

df = pd.read_csv("topcv_data_analyst_jobs.csv")
print(df.shape)
print(df.columns)

# Lọc job ở TP.HCM, có “Python” trong mô tả yêu cầu
mask_hcm = df["detail_location"].fillna("").str.contains("Hồ Chí Minh", case=False)
mask_py  = df["desc_yeucau"].fillna("").str.contains("Python", case=False)
df_filtered = df[mask_hcm & mask_py]
df_filtered.head()
```

Xuất XLSX:

```python
df.to_excel("topcv_data_analyst_jobs.xlsx", index=False)
```

---

## 🧩 Các cột chính

* **Job (search):** `title`, `job_url`, `company`, `company_url`, `salary_list`, `address_list`, `exp_list`
* **Job (detail):** `detail_title`, `detail_salary`, `detail_location`, `detail_experience`, `deadline`, `tags`,
  `desc_mota`, `desc_yeucau`, `desc_quyenloi`, `working_addresses`, `working_times`, `company_url_from_job`
* **Company:** `company_name_full`, `company_website`, `company_size`, `company_industry`, `company_address`, `company_description`

> `company_url_from_job` có thể khác `company_url` (ưu tiên link trên trang job nếu có).

---

## 🧰 Troubleshooting

* **429 Too Many Requests**
  Tăng delay (xem phần “Điều chỉnh tốc độ”), giảm số trang, chạy chậm lại.

* **HTML thay đổi**
  DOM của TopCV có thể update. Ưu tiên các selector “dựa trên tiêu đề” (ví dụ `Mức lương`, `Địa điểm`, `Kinh nghiệm`) để giảm rủi ro vỡ.

* **Selenium & Chrome**
  Chỉ cần nếu bạn muốn bắt network nâng cao hoặc trang render mạnh bằng JS. Script hiện tại không phụ thuộc Selenium.

---

## 🗺️ Lộ trình mở rộng

* Thêm phân loại keyword (Python/SQL/BI, v.v.) từ mô tả yêu cầu.
* Chuẩn hóa địa điểm/tỉnh thành, chuẩn hoá mức lương.
* Lưu DB (SQLite/Postgres) + incremental update theo `job_id`.
* Thêm CLI flag: `--start-page`, `--end-page`, `--delay-min`, `--delay-max`, `--query`.

---

## 📄 License

MIT — dùng thoải mái cho mục đích học tập & nghiên cứu.
**Lưu ý:** Hãy tôn trọng điều khoản sử dụng của TopCV và không gây tải lớn lên hệ thống.

---
