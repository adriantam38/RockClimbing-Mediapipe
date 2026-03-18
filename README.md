# 🧗 Rock Climbing Motion Analysis System

A high-performance desktop application built with **Python**, **OpenCV**, and **MediaPipe** designed for real-time skeletal tracking, route visualization, and performance analytics in rock climbing.



## 📖 Project Overview

This system provides a professional interface for climbers to analyze their technique. By using computer vision to overlay skeletal data onto live video feeds, users can identify center-of-gravity shifts, reach efficiency, and movement patterns.

The application uses a modular **View-driven architecture**, allowing for seamless transitions between live camera tracking, video review, and data settings.

---

## ✨ Key Features

* **Real-time AI Analysis:** Integrated `CameraView` using **MediaPipe Pose** to track 33 body landmarks.
* **Intelligent Navigation:** A custom `Maps()` system that manages memory by toggling view visibility (`place_forget`).
* **Dynamic UI Scaling:** Automatically detects monitor resolution via `ctypes` for a pixel-perfect fullscreen experience.
* **Keypad Optimized:** Specialized `ControlBar` logic allowing for interaction via physical keypads (with a "Reverse Mode" toggle).
* **Session Management:** Save and load climbing data through the `SaveLoadModule`.
* **Multi-language Support:** Powered by `python-i18n` with JSON-based localization.

---

## 🚀 Getting Started

### Prerequisites

* Windows 10/11 (for `ctypes` screen metrics)
* Python 3.8+
* A high-definition webcam or IP camera

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/rock-climbing-analysis.git](https://github.com/yourusername/rock-climbing-analysis.git)
   cd rock-climbing-analysis
