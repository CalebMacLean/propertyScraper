# Lord Tracker
Web Interface for the Housing Trends in Washoe County Nevada

## Features
- Search owners by name, company, properties.
- Identify top 10 largest property owners.
- Search through data by category.

## Application Summary
A user of the site is met with a table listing the top land owners in Washoe county, this data is collected dynamically everytime the site is loaded.
This site is a tool for finding public owner data so the navigation bar has many ways to search through information. The site logo acts as a home page button that returns to the top 10 ownership table.
The navigation buttons will pull up a paginated list of results seperated by category. Finally, for more specific results the user is able to make queries to the database using the search bar, the search bar will find
the top 10 most similar results to the query (case insensitive). The purpose of the site is to connect the user to owner data so all properties, owner and company names act as links to the related owner information page.

This application is essentially two seperate applications working towards a unified goal. The single page application provides an interface for users to easily find owner data, while the second application acts a web scraper that collects the
information for the database.

## Supporting Technologies
Both technologies use various supportive languages, frameworks and libraries

### Languages
- Python
- JavaScript
- HTML
- CSS
- SQL

### Technologies
- PostgreSQL
- Flask
- SQLAlchemy
- Bootstrap
- jQuery
- Google Fonts

## Important Note
Currently external factors are not allowing the application to run, but updates will be made once the web scraper is allowed to resume its function.

