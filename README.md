# ✈️ PyFly - Flight Reservation System

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Django](https://img.shields.io/badge/Django-4.x-green?style=flat&logo=django)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?style=flat&logo=sqlite)

**PyFly** is a comprehensive web-based flight booking application designed to simulate real-world airline operations. Built with **Django**, it streamlines the entire process from flight scheduling to passenger baggage management.

## 📖 Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technical Highlights](#technical-highlights)
- [Installation & Setup](#installation--setup)
- [Technologies Used](#technologies-used)
- [Team](#team)

---

## 🚀 Project Overview
PyFly provides a robust platform for users to search for flights, book tickets, and manage their travel details. Unlike standard booking systems, PyFly includes a detailed backend logic for **logistics and baggage handling**, ensuring a seamless data flow between passenger manifests and cargo limitations.

## ✨ Key Features
* **User Authentication:** Secure login/register system for passengers and admins.
* **Flight Search & Filter:** Dynamic filtering by date, destination, and price.
* **Seat Selection:** Interactive seat map for choosing specific seats.
* **Ticket Management:** View, download, and cancel bookings.
* **Admin Dashboard:** Full control over flight schedules, planes, and pricing.

## 🧳 Technical Highlights: Baggage Management Module
*Special focus was placed on the backend logic for baggage operations:*
* **Weight Calculation Logic:** Automatically calculates total baggage weight per passenger and applies dynamic pricing for excess weight.
* **Passenger-Luggage Matching:** Relational database models linking specific luggage IDs to passenger tickets to prevent data mismatches.
* **Lost Baggage Tracking:** A dedicated system for reporting and tracking status updates for mishandled luggage.

---

## 🛠 Installation & Setup

To run this project locally, follow these steps:

1. **Clone the repository:**
2. **Open Terminal:**
4. **Apply database migrations:**
python manage.py runserver
5. **Run the server:**
python manage.py runserver
Access the app at http://127.0.0.1:8000/

## 💻 Technologies Used
Backend: Python, Django Framework

Database: SQLite (Development)

Frontend: HTML5, CSS3, JavaScript

Version Control: Git

## 👥 Team
This project was developed as a collaborative effort by:

Ege Kaan Kıcı (Backend & Baggage Logic)

Burak

Emre

Yusuf

Bengü
