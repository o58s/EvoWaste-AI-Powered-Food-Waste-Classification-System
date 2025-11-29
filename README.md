# EvoWaste — AI-Powered Food Waste Classification System

EvoWaste is a full-stack AI application designed to classify and track food waste using real-time image recognition. The system uses a custom YOLO model trained on a Roboflow dataset I created, enabling accurate classification into four categories: Edible, Animal Feed, Compostable, and Non-Reusable.

Throughout development, I debugged backend logic, database workflows, file handling, and YOLO predictions to ensure smooth and reliable performance. EvoWaste also includes a full user system, personal history tracking, and a modern interactive UI powered by JavaScript.

## Features

### AI Waste Classification
Upload an image and let the YOLO model predict the waste category with confidence scores.

### History Tracking
Every classification is saved with:

Date & Time
Predicted Category
Confidence
User Location
Image Preview

### Location-Based Insights
Captures user location for potential analytics and heat-map visualization.


### User System

Sign up
Login
Profile editing

### MySQL Database Integration

Stores users, classifications, timestamps, and image paths.

### Modern UI/UX

Drag-&-drop image upload
Animated loaders
Dynamic result display

## Tech Stack

Backend: Python, Flask
AI Model: YOLO (Ultralytics)
Database: MySQL
Frontend: HTML, CSS, JavaScript
Tools: Roboflow (for dataset creation & annotation)

## Installation & Setup

Follow the steps below to run EvoWaste locally.

### Prerequisites

Make sure you have installed:
Python 3.9+
pip
MySQL Server
Git
YOLO model file (best.pt)

### Folder Structure

EvoWaste/
│── app.py
│── model.pt
│── /static
│     ├── style.css/
│     └── uploads/
│── /templates
│     ├── signup.html
│     ├── login.html
│     ├── home.html
│     └── upload.html
│     ├── history.html
│     ├── profile.html



YOLO model file (best.pt)
