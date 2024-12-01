from multiprocessing import Process, Manager
from crewai import Agent, Task, Crew, Process as CrewProcess, LLM
import os
from typing import Dict, Any

class SEOAnalyzer:
    def __init__(self):
        self.manager_llm = LLM(
            model="claude-3-5-sonnet-20241022", 
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        self.keyword_agent = self._create_keyword_agent()
        self.summary_agent = self._create_summary_agent()
        self.headline_agent = self._create_headline_agent()
        self.content_generator_agent = self._create_content_generator_agent()

    def _create_keyword_agent(self) -> Agent:
        """Create and return the keyword analysis agent."""
        return Agent(
            role='SEO Keyword Specialist',
            goal='Extract relevant SEO keywords from blog content',
            backstory='Expert in SEO keyword analysis and content optimization',
            allow_delegation=False,
            verbose=True,
            llm=LLM(
                model="claude-3-5-sonnet-20241022", 
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        )

    def _create_summary_agent(self) -> Agent:
        """Create and return the summary agent."""
        return Agent(
            role='Content Summary Analyst',
            goal='Generate a concise summary of the blog content',
            backstory='Expert in summarizing content effectively',
            allow_delegation=False,
            verbose=True,
            llm=LLM(
                model="claude-3-5-sonnet-20241022", 
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        )

    def _create_headline_agent(self) -> Agent:
        """Create and return the headline extraction agent."""
        return Agent(
            role='Content Structure Analyst',
            goal='Extract headlines and key points from blog content',
            backstory='Expert in content analysis and structure identification',
            allow_delegation=False,
            verbose=True,
            llm=LLM(
                model="claude-3-5-sonnet-20241022", 
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        )

    def _create_content_generator_agent(self) -> Agent:
        """Create and return the content generation agent."""
        return Agent(
            role="""A
You are a talented content writer and SEO expert for LotusTherapy, a clinical psychology practice. Your task is to create an SEO-optimized article about a mental health topic that feels warm, relatable, and inviting, appealing to individuals searching for support with mental health challenges in Vancouver.
Background Information:
* About Lotus Therapy & Counselling Centre: At Lotus Therapy, we believe in the power of connection, compassion, and the courage it takes to heal. Our team of skilled therapists provides a safe and welcoming space to explore emotions and embrace growth. Specializing in anxiety, depression, ADHD, trauma, and more, we offer a holistic and trauma-informed approach to mental health care. Services are available in Vancouver, Coquitlam, and online.""",
            goal='Generate SEO-optimized content based on keywords and structure',
            backstory='Expert content writer specializing in SEO-optimized articles',
            allow_delegation=False,
            verbose=True,
            llm=LLM(
                model="claude-3-5-sonnet-20241022", 
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        )

    def _extract_keywords(self, text: str, return_dict: Dict[str, Any]) -> None:
        """Extract keywords from the given text using CrewAI."""
        try:
            keyword_task = Task(
                description=f"Extract key SEO keywords from this text. Return only a comma-separated list of keywords: {text}",
                agent=self.keyword_agent,
                expected_output="A comma-separated list of SEO keywords"
            )

            crew_keywords = Crew(
                agents=[self.keyword_agent],
                tasks=[keyword_task],
                verbose=True,
                process=CrewProcess.sequential,
                planning=True,
                planning_llm=self.manager_llm
            )

            result = crew_keywords.kickoff()
            if result:
                # Clean up the result by removing any extra whitespace and newlines
                keywords = result.raw
                return_dict['keywords'] = keywords
            else:
                return_dict['keywords'] = "No keywords found"
        except Exception as e:
            print(f"Error in keyword extraction: {str(e)}")
            return_dict['keywords'] = f"Error extracting keywords: {str(e)}"

    def _generate_summary(self, text: str, return_dict: Dict[str, Any]) -> None:
        """Generate a summary of the given text using CrewAI."""
        summary_task = Task(
            description=f"Create a concise 2-3 sentence summary of this text that captures its main points: {text}",
            agent=self.summary_agent,
            expected_output="A concise summary of the text"
        )

        crew_summary = Crew(
            agents=[self.summary_agent],
            tasks=[summary_task],
            verbose=True,
            process=CrewProcess.sequential,
            planning=True,
            planning_llm=self.manager_llm
        )

        summary = crew_summary.kickoff()
        try:
            return_dict['summary'] = summary.raw
        except Exception as e:
            return_dict['summary'] = "Error parsing summary"

    def _extract_headlines_and_keypoints(self, text: str, return_dict: Dict[str, Any]) -> None:
        """Extract headlines and key points from the given text using CrewAI."""
        try:
            headline_task = Task(
                description=(
                    "Analyze this text and extract:\n"
                    "1. All headlines/subheadings\n"
                    "2. Key points under each headline\n"
                    f"Text: {text}\n"
                    "Format the output as a structured list with headlines and their corresponding key points."
                ),
                agent=self.headline_agent,
                expected_output="A structured list of headlines and key points"
            )

            crew_headlines = Crew(
                agents=[self.headline_agent],
                tasks=[headline_task],
                verbose=True,
                process=CrewProcess.sequential,
                planning=True,
                planning_llm=self.manager_llm
            )

            result = crew_headlines.kickoff()
            return_dict['headlines_and_keypoints'] = result.raw
        except Exception as e:
            print(f"Error in headline extraction: {str(e)}")
            return_dict['headlines_and_keypoints'] = f"Error extracting headlines: {str(e)}"

    def _generate_new_article(self, headlines_and_keypoints: str, keywords: str, return_dict: Dict[str, Any]) -> None:
        """Generate a new SEO-optimized article based on extracted information."""
        try:
            content_task = Task(
                description=(
                    "Your Task:\n"
                    f"1. Headlines and Key Points: {headlines_and_keypoints}\n"
                    f"2. Target Keywords: {keywords}\n"
                    "2. Guidelines:\n"
                    "   * Length: 1,000-1,500 words\n" 
                    "   * Tone: Friendly, relational, and approachable\n"
                    "   * Perspective: Third-person language\n"
                    "   * Keyword: holiday anxiety counselling\n"
                    "Instructions:\n"
                    "1. Planning Phase *(Enclosed within *<article_planning> tags):\n"
                    "   a. Outline the article structure with a focus on building a narrative that feels empathetic and supportive.\n"
                    "   b. Identify key points for each section that resonate emotionally with readers.\n"
                    "   c. Plan keyword placement and craft a meta description designed to feel warm and inviting.\n"
                    "   d. Generate two distinct article headlines - one optimized for SEO and one focused on capturing the emotional essence.\n"
                    "2. Writing Phase *(Enclosed within *<article> tags):\n"
                    "   * Title Options:\n"
                    "     - SEO Title: A concise, friendly title (max 60 chars) incorporating the main keyword\n"
                    "     - Alternative Title: An emotionally resonant title that captures the article's essence\n"
                    "   * Meta Description: A relational meta description under 130 characters using the main keyword, designed to draw in readers.\n"
                    "   * Body: Use H2 and H3 headings to create an organized, yet conversational flow. Include internal links to LotusTherapy.ca naturally. Focus on providing helpful insights while maintaining a relatable, compassionate tone.\n"
                    "Special Guidance: Subtly integrate principles from methods like EMDR, somatic experiencing, and related therapies (without directly naming them) to present a holistic, supportive approach to anxiety management. Use relatable examples, calming imagery, and inclusive language to make the reader feel understood and supported.\n"
                    "Note: Present both title options at the start of the article, with a recommendation for which to use based on the target audience and emotional impact."
                ),
                agent=self.content_generator_agent,
                expected_output="A complete SEO-optimized article with two strategic title options"
            )

            crew_content = Crew(
                agents=[self.content_generator_agent],
                tasks=[content_task],
                verbose=True,
                process=CrewProcess.sequential,
                planning=True,
                planning_llm=self.manager_llm
            )

            result = crew_content.kickoff()
            return_dict['generated_article'] = result.raw
        except Exception as e:
            print(f"Error in article generation: {str(e)}")
            return_dict['generated_article'] = f"Error generating article: {str(e)}"

    def analyze_content(self, text: str) -> Dict[str, str]:
        """
        Analyze the content and generate a new SEO-optimized article.
        
        Args:
            text (str): The text content to analyze
            
        Returns:
            Dict[str, str]: Dictionary containing keywords, headlines, and generated article
        """
        manager = Manager()
        return_dict = manager.dict()

        # Extract keywords and headlines in parallel
        p1 = Process(target=self._extract_keywords, args=(text, return_dict))
        p2 = Process(target=self._extract_headlines_and_keypoints, args=(text, return_dict))

        # Start the processes
        p1.start()
        p2.start()

        # Wait for both processes to finish
        p1.join()
        p2.join()

        # Generate new article after getting keywords and headlines
        p3 = Process(target=self._generate_new_article, 
                    args=(return_dict.get('headlines_and_keypoints', ''),
                         return_dict.get('keywords', ''),
                         return_dict))
        p3.start()
        p3.join()

        return {
            'keywords': return_dict.get('keywords', ''),
            'headlines_and_keypoints': return_dict.get('headlines_and_keypoints', ''),
            'generated_article': return_dict.get('generated_article', '')
        } 