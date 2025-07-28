# **Technical Design Document: Zendesk Data Extraction**

## **1\. Introduction**

This document outlines the technical design for a solution to extract historical customer conversation data from Zendesk. The current method of manually requesting data from Zendesk support is not scalable, is time-consuming, and lacks the necessary flexibility for querying.

The proposed solution is to build a data pipeline that programmatically extracts ticket data, including the full conversation history, using the Zendesk API. This will enable the data to be used for AI/ML modeling (e.g., sentiment analysis, topic modeling) and for manual review in a human-readable format.

## **2\. Goals**

* **Primary Goal:** To build an automated and scalable data pipeline to extract complete customer conversation data from Zendesk.  
* **Secondary Goal:** To provide the extracted data in two formats:  
  * **JSON:** For ingestion into AI/ML models and other data systems.  
  * **XML:** For manual review by internal teams.

## **3\. Non-Goals**

* This project will not include the development of the AI/ML models themselves.  
* This solution will not provide a real-time data stream. The extraction will be done in batches.  
* This design does not cover the user interface for initiating or monitoring the extraction process, though one could be built on top of this core logic.

## **4\. System Architecture**

The proposed system will be a script-based solution, likely written in Python due to its strong data manipulation libraries and ease of use for API interactions. The architecture will be composed of the following components:

1. **Authentication Module:** Securely handles authentication with the Zendesk API using an API token.  
2. **Extraction Module:**  
   * Fetches a list of ticket IDs based on specified criteria (e.g., date range).  
   * For each ticket ID, it retrieves the full ticket details, including all associated comments (the conversation history).  
3. **Transformation Module:**  
   * Processes the raw JSON data from the API.  
   * Structures the data into a clean, well-defined JSON format.  
   * Converts the JSON data into an equivalent XML format.  
4. **Storage Module:**  
   * Saves the extracted and transformed data to a local or cloud-based storage solution (e.g., local file system, Amazon S3, Google Cloud Storage).

### **Diagram**

\+----------------------+      \+----------------------+      \+------------------------+      \+---------------------+  
|                      |      |                      |      |                        |      |                     |  
|   Zendesk API        \<-----\>|  Extraction Script   |-----\>|  Transformation Module |-----\>|  Storage (JSON/XML) |  
| (Tickets & Comments) |      |   (Python)           |      |  (JSON \-\> XML)         |      |                     |  
\+----------------------+      \+----------------------+      \+------------------------+      \+---------------------+  
        ^  
        |  
\+----------------------+  
|  Authentication      |  
|  (API Token)         |  
\+----------------------+

## **5\. Zendesk API Endpoints**

A preliminary investigation of the Zendesk API documentation confirms that the necessary endpoints are available.

* **Authentication:** We will use API Token authentication. The token will be passed in the request header.  
* **Tickets:** The GET /api/v2/tickets endpoint can be used to retrieve a list of tickets. We can filter by date and other parameters.  
* **Ticket Comments:** The GET /api/v2/tickets/{ticket\_id}/comments endpoint will be used to retrieve all the comments for a specific ticket. This is the key to getting the full conversation history.

## **6\. Data Model**

The extracted data will be stored in a structured JSON format. Each JSON file will represent a single Zendesk ticket.

### **JSON Schema Example:**

{  
  "ticket\_id": 12345,  
  "created\_at": "2023-10-27T10:30:00Z",  
  "updated\_at": "2023-10-27T12:00:00Z",  
  "subject": "Issue with billing",  
  "status": "closed",  
  "requester\_id": 98765,  
  "assignee\_id": 54321,  
  "tags": \["billing", "invoice"\],  
  "conversation": \[  
    {  
      "comment\_id": 111,  
      "author\_id": 98765,  
      "body": "Hello, I have a question about my recent invoice.",  
      "created\_at": "2023-10-27T10:30:00Z"  
    },  
    {  
      "comment\_id": 222,  
      "author\_id": 54321,  
      "body": "Hi there, I can help with that. What is your question?",  
      "created\_at": "2023-10-27T10:35:00Z"  
    }  
  \]  
}

### **XML Format**

The XML format will mirror the JSON structure.

\<ticket\>  
  \<ticket\_id\>12345\</ticket\_id\>  
  \<created\_at\>2023-10-27T10:30:00Z\</created\_at\>  
  \<updated\_at\>2023-10-27T12:00:00Z\</updated\_at\>  
  \<subject\>Issue with billing\</subject\>  
  \<status\>closed\</status\>  
  \<requester\_id\>98765\</requester\_id\>  
  \<assignee\_id\>54321\</assignee\_id\>  
  \<tags\>  
    \<tag\>billing\</tag\>  
    \<tag\>invoice\</tag\>  
  \</tags\>  
  \<conversation\>  
    \<comment\>  
      \<comment\_id\>111\</comment\_id\>  
      \<author\_id\>98765\</author\_id\>  
      \<body\>Hello, I have a question about my recent invoice.\</body\>  
      \<created\_at\>2023-10-27T10:30:00Z\</created\_at\>  
    \</comment\>  
    \<comment\>  
      \<comment\_id\>222\</comment\_id\>  
      \<author\_id\>54321\</author\_id\>  
      \<body\>Hi there, I can help with that. What is your question?\</body\>  
      \<created\_at\>2023-10-27T10:35:00Z\</created\_at\>  
    \</comment\>  
  \</conversation\>  
\</ticket\>

## **7\. Implementation Details**

* **Language:** Python 3.x  
* **Libraries:**  
  * requests: For making HTTP requests to the Zendesk API.  
  * json: For handling JSON data.  
  * xml.etree.ElementTree: For creating the XML files.  
  * python-dotenv: For managing API keys and other configuration variables securely.  
* **Configuration:** A separate configuration file (e.g., .env) will store the Zendesk API endpoint, API token, and other settings. This prevents hardcoding sensitive information in the script.  
* **Error Handling:** The script will include robust error handling to manage API rate limits, network issues, and invalid data.  
* **Logging:** The script will log its progress, including the number of tickets processed and any errors encountered.

## **8\. Security Considerations**

* The Zendesk API token is a sensitive credential and must be stored securely. It should not be committed to version control. Using a .env file and adding it to .gitignore is a good practice.  
* Access to the extracted data should be restricted to authorized personnel.

## **9\. Future Enhancements**

* **Incremental Backups:** The script could be modified to only fetch tickets that have been updated since the last run.  
* **Web Interface:** A simple web interface could be built to allow non-technical users to initiate the extraction process and download the data.  
* **Database Integration:** The extracted data could be loaded directly into a database (e.g., PostgreSQL, BigQuery) for more advanced querying and analysis.

This TDD provides a comprehensive plan for developing a solution to the Zendesk data extraction problem. The proposed approach is technically feasible, scalable, and meets all the requirements outlined in the project plan.
