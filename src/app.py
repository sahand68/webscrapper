import streamlit as st
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

from scraper.blog_scraper import BlogScraper
from analyzer.seo_analyzer import SEOAnalyzer

# Load environment variables
load_dotenv()

def analyze_content_async(analyzer: SEOAnalyzer, content: str, analysis_type: str) -> Dict[str, Any]:
    """Run specific analysis asynchronously."""
    from multiprocessing import Manager
    manager = Manager()
    return_dict = manager.dict()
    
    if analysis_type == 'keywords':
        analyzer._extract_keywords(content, return_dict)
        return {'keywords': return_dict.get('keywords', '')}
    elif analysis_type == 'headlines':
        analyzer._extract_headlines_and_keypoints(content, return_dict)
        return {'headlines_and_keypoints': return_dict.get('headlines_and_keypoints', '')}
    elif analysis_type == 'generate_article':
        # First get keywords and headlines if not already present
        if not return_dict.get('keywords'):
            analyzer._extract_keywords(content, return_dict)
        if not return_dict.get('headlines_and_keypoints'):
            analyzer._extract_headlines_and_keypoints(content, return_dict)
        
        # Generate the article
        analyzer._generate_new_article(
            return_dict.get('headlines_and_keypoints', ''),
            return_dict.get('keywords', ''),
            return_dict
        )
        return {
            'keywords': return_dict.get('keywords', ''),
            'headlines_and_keypoints': return_dict.get('headlines_and_keypoints', ''),
            'generated_article': return_dict.get('generated_article', '')
        }
    return {}

def show_blog_list():
    """Display the list of blog posts and scraping interface."""
    st.title("Blog SEO Analyzer")
    st.write("Analyze blog posts and generate SEO insights")

    # URL input and number of posts selector in a single row
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input(
            "Enter the blog URL to analyze:", 
            "https://wellbeingscounselling.ca/blog/"
        )
    with col2:
        num_posts = st.number_input(
            "Number of posts to scrape:", 
            min_value=1, 
            max_value=100, 
            value=10
        )
    
    # Initialize components
    scraper = BlogScraper()

    if st.button("Scrape Blog Posts"):
        with st.spinner("Scraping blog posts..."):
            blog_posts = scraper.scrape_blogs(url, num_posts)
            if blog_posts:
                st.session_state['blog_posts'] = blog_posts
                st.success(f"Found {len(blog_posts)} blog posts!")
            else:
                st.warning(
                    "No blog posts found. Try adjusting the URL or check if the website is accessible."
                )

    if 'blog_posts' in st.session_state:
        st.subheader("Blog Posts")
        
        for index, post in enumerate(st.session_state['blog_posts']):
            # Create a clickable title that sets the selected post
            if st.button(f"{index+1}. {post['title']}", key=f"post_{index}"):
                st.session_state['selected_post'] = index
                st.session_state['page'] = 'detail'
                st.rerun()

def show_blog_detail():
    """Display detailed analysis for a selected blog post."""
    if 'selected_post' not in st.session_state:
        st.session_state['page'] = 'list'
        st.rerun()
        return

    post = st.session_state['blog_posts'][st.session_state['selected_post']]
    
    # Add a back button
    if st.button("← Back to Blog List"):
        st.session_state['page'] = 'list'
        st.rerun()
        return

    st.title(post['title'])
    st.write("**Link:**", post['link'])
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Content", "Keywords", "Headlines & Key Points", "Generated Article"])
    
    with tab1:
        st.subheader("Blog Content")
        st.write(post['excerpt'])
    
    with tab2:
        st.subheader("Keywords Analysis")
        content = f"Title: {post['title']}\n\nExcerpt: {post['excerpt']}"
        
        if not post.get('keywords'):
            if st.button("Extract Keywords", key="analyze_keywords"):
                with st.spinner("Extracting keywords..."):
                    analyzer = SEOAnalyzer()
                    result = analyze_content_async(analyzer, content, 'keywords')
                    post.update(result)
                    st.rerun()
        
        if post.get('keywords'):
            st.write(post['keywords'])
    
    with tab3:
        st.subheader("Headlines and Key Points")
        if not post.get('headlines_and_keypoints'):
            if st.button("Extract Headlines", key="analyze_headlines"):
                with st.spinner("Extracting headlines and key points..."):
                    analyzer = SEOAnalyzer()
                    result = analyze_content_async(analyzer, content, 'headlines')
                    post.update(result)
                    st.rerun()
        
        if post.get('headlines_and_keypoints'):
            st.write(post['headlines_and_keypoints'])
    
    with tab4:
        st.subheader("Generated SEO-Optimized Article")
        if st.button("Generate New Article", key="generate_article"):
            with st.spinner("Generating SEO-optimized article..."):
                analyzer = SEOAnalyzer()
                result = analyze_content_async(analyzer, content, 'generate_article')
                post.update(result)
                st.rerun()
        
        if post.get('generated_article'):
            st.write(post['generated_article'])

def main():
    """Main application function."""
    # Set page config
    st.set_page_config(page_title="Blog SEO Analyzer", layout="wide")
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state['page'] = 'list'
    
    # Show appropriate page
    if st.session_state['page'] == 'list':
        show_blog_list()
    else:
        show_blog_detail()

if __name__ == "__main__":
    main() 