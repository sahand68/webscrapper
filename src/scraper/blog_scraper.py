import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import streamlit as st

class BlogScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def is_valid_url(self, url: str) -> bool:
        """Validate if the given URL is properly formatted."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def get_page_content(self, url: str) -> bytes | None:
        """Fetch content from the given URL."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.content
        except Exception as e:
            st.error(f"Error fetching URL: {str(e)}")
            return None

    def scrape_blogs(self, url: str, num_posts: int) -> list[dict]:
        """
        Scrape blog posts from the given URL.
        
        Args:
            url (str): The URL to scrape from
            num_posts (int): Number of posts to scrape
            
        Returns:
            list[dict]: List of blog post dictionaries containing title, link, and excerpt
        """
        if not self.is_valid_url(url):
            st.error("Please enter a valid URL")
            return []
            
        try:
            blog_posts = []
            content = self.get_page_content(url)
            if not content:
                return []

            soup = BeautifulSoup(content, 'html.parser')
            articles = soup.find_all('article', class_='elementor-post')
            
            for article in articles[:num_posts]:
                # Find title
                title_elem = article.find(['h2', 'h3'], class_='elementor-post__title')
                title = title_elem.text.strip() if title_elem else ""

                # Find link
                link_elem = title_elem.find('a') if title_elem else None
                link = link_elem.get('href', '') if link_elem else ""

                # Find excerpt
                excerpt_elem = article.find('div', class_='elementor-post__excerpt')
                excerpt = excerpt_elem.text.strip() if excerpt_elem else ""

                if title or excerpt:  # Only add if we have at least a title or excerpt
                    blog_posts.append({
                        'title': title,
                        'link': link,
                        'excerpt': excerpt,
                        'keywords': '',  # Initialize with empty string
                        'summary': '',   # Initialize with empty string
                        'analyzed': False  # Track if post has been analyzed
                    })
            
            return blog_posts
        except Exception as e:
            st.error(f"Error scraping blogs: {str(e)}")
            return [] 