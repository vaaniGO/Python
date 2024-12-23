This file contains codes for various Ai-based Agents to perform customisable web-scraping efficiently through optimising micro-tasks.
1. Ollama scraper with pandas includes extracting web-links from a pandas dataframe, and dumping the description into the next column of the dataframe
2. Ollama scraper with beautiful soup and Google Sheets integration includes accessing a Google Sheet using service account credentials, reading links in the sheet, extracting only their meta-descriptions using beautiful soup, and then using the LLM (ollama) on the extracted descriptions to summarise them, and dump them back alongside the corresponding links on the same Google Sheet.

