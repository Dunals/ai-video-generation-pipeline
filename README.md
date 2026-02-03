# AI Video Generation Pipeline (Proxy-Rotated)

This project implements a robust automation pipeline to interact with public AI video generation APIs (Hugging Face Spaces). It features a high-performance proxy rotation system and direct Gradio backend interaction to generate video content from images reliability.

## 🚀 Key Features

* **Multi-Threaded Proxy Scanning:** concurrently scans and verifies hundreds of HTTP/S proxies using `concurrent.futures` to ensure low-latency connections.
* **Gradio API Reverse Engineering:** Manually handles the full lifecycle of the Gradio backend: File Upload -> Job Queuing -> Event Streaming -> Content Download.
* **Fault Tolerance:** Automatically switches proxies upon request failure or timeout, ensuring high availability for long-running tasks.
* **Wan2.0 Model Integration:** specifically configured to interface with the Wan2.0 Image-to-Video model endpoints.

## 🛠 Dependencies

* Python 3.x
* `requests`

## 📂 Setup & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/ai-video-generation-pipeline.git](https://github.com/yourusername/ai-video-generation-pipeline.git)
    cd ai-video-generation-pipeline
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Prepare Input:**
    Place your source image named `1.jpg` in the root directory (or modify the `IMAGE_PATH` variable in the script).

4.  **Run the Pipeline:**
    ```bash
    python main.py
    ```

## ⚙️ How It Works

1.  **Proxy Acquisition:** Scrapes fresh public proxy lists from GitHub sources.
2.  **Speed Test:** Spawns 300 threads to identify the fastest working proxy for the specific AI endpoint.
3.  **Job Execution:** * Uploads the image to the temporary file server.
    * Joins the processing queue with specific generation parameters.
    * Listens for Server-Sent Events (SSE) to track progress.
4.  **Download:** Retrieves the final MP4 video using the same active proxy session.

## ⚠️ Disclaimer

This tool is for educational purposes and demonstrates network automation techniques. Please use public APIs responsibly and adhere to their terms of service.
