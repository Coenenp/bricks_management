# Brick Collection Management System

![android-chrome-512x512](https://github.com/Coenenp/bricks_management/assets/17593262/bf9d3a69-f3a9-4a65-ac18-b873d1dc97cb)

## Overview

The Brick Collection Management System is a Django-based inventory system designed to organize Lego bricks and custom designs (MOC). The system enables users to manage their brick collections, track parts, and cross-reference against set lists to identify missing pieces required to complete sets.

## User Interface Preview

![Dashboard_1](https://github.com/Coenenp/bricks_management/assets/17593262/14b3bdf3-62dc-4653-acda-8e1ca807d8fb)
*Screenshot: Dashboard displaying the user's collection filtered by color and type*

![Itemview_1](https://github.com/Coenenp/bricks_management/assets/17593262/6a990e9a-a822-470b-986d-c8b06c7f9179)
*Screenshot: Item View showcasing available molds or items*

## Key Concepts

- **Items**: Represent available brick designs.
- **Parts**: Denote items in specific colors, added within lists to track their origin (e.g., a set).
- **Lists**: Manage and categorize parts, associating them with sources (e.g., sets).
- **Sets**: Full sets or instructions uploaded for comparison against available parts.

## User Workflow

1. **Access**: Enter the system via a splash page with a "Get Started" button, leading to a login page.
2. **Authentication**: Sign up for an account or log in to access the Dashboard.
3. **Dashboard**: Comprehensive view of the user's collection, allowing filtering and viewing parts or aggregated parts.
4. **Functionalities**:

    - **Add New Parts**: Include new parts specifying item, color, list, and quantity.
    - **Delete Parts**: Remove parts from specific lists or all lists based on the view.
    - **Part Details**: View detailed part information, including lists associated and quantity adjustments.
    - **Item View**: Display available molds or items, toggle between grid and table views, and manage items.
    - **Set List View**: Access and view all uploaded or added sets with respective actions.
    - **Set Details View**: Detailed view of a specific set, including associated parts and availability details.
    - **List View**: Display a table of all lists with key details such as ID, Name, Description, and item counts.

## Additional Packages

Below are the additional packages installed for this Django project:

- **django-fontawesome-5**: Integration for Font Awesome icons in Django templates.
- **python-decouple**: Simplifies handling of settings by separating configuration from code.
- **crispy_forms**: Assists in managing Django forms elegantly.
- **crispy_bootstrap5**: Extends crispy_forms to utilize Bootstrap 5 styles for forms.

## Front-end Framework and Theme

This project utilizes Bootstrap 5 as the front-end framework with the "Minty" theme obtained from Bootswatch. Bootstrap 5 ensures a responsive and visually appealing user interface.

## Usage

To deploy and run the project locally:

1. Clone this repository.
2. Install dependencies by running `pip install -r requirements.txt`.
3. Set up the Django environment and database.
4. Run the development server using `python manage.py runserver`.
5. Access the application via a web browser at `http://localhost:8000`.

## Contributors

- Pieter Coenen - Project Lead & Developer

## Acknowledgments

- Legion Script for the initial tutorial ([link](https://www.youtube.com/watch?v=_sWgionzDoM&ab_channel=LegionScript)) that kickstarted the project.

Feel free to contribute, report issues, or suggest enhancements!