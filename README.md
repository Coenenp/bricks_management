# Brick Collection Management System

![android-chrome-192x192](https://github.com/Coenenp/bricks_management/assets/17593262/f9addcc5-68b4-45c5-8631-bc868d46eb23)

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
    - **Item Details View**: Showcases an image of the item in a random color and relevant details such as Item ID and name. Allows users to create new parts by selecting a color from the matrix, choosing a list, specifying a positive quantity, and adding it to the selected list. Displays a table of related parts and their respective lists. Users can navigate to the part details page or delete the part, removing it from all lists.
    - **Set List View**: Access and view all uploaded or added sets with respective actions.
    - **Set Details View**: Detailed view of a specific set, including associated parts and availability details.
    - **List View**: Display a table of all lists with key details such as ID, Name, Description, and item counts.

## Additional Packages

Below are the additional packages installed for this Django project:

- **django-fontawesome-5**: Integration for Font Awesome icons in Django templates.
- **python-decouple**: Simplifies handling of settings by separating configuration from code.
- **django-crispy-forms**: Assists in managing Django forms elegantly.
- **crispy-bootstrap5**: Extends crispy_forms to utilize Bootstrap 5 styles for forms.
- **pandas**: Provides data manipulation and analysis tools in Python.
- **Pillow**: Python Imaging Library for handling image files.

## Front-end Framework and Theme

This project utilizes Bootstrap 5 as the front-end framework with the "Minty" theme obtained from Bootswatch. Bootstrap 5 ensures a responsive and visually appealing user interface.

## Public Domain Dedication

All code and subsequent modifications in this project have been created by Pieter Coenen and are hereby released into the public domain. To the extent possible under law, I waive all copyright and related or neighboring rights to this work worldwide.

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
