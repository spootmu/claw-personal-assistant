"""
Task to periodically scrape 58同城 for office building data
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from data_scraper import DataScraper


class PropertyScrapingTask:
    """Task for scraping property data from 58同城"""
    
    def __init__(self, assistant):
        self.assistant = assistant
        self.logger = logging.getLogger(f"{assistant.name}.PropertyScrapingTask")
        self.is_running = False
        
    async def run(self):
        """Main execution method for the task"""
        self.logger.info("Starting property scraping task")
        self.is_running = True
        
        try:
            # Example: Scrape office buildings in Nanjing with min price of 5 million
            listings = await self.assistant.scrape_58_tongcheng_data(
                city="nj",
                min_price=5000000
            )
            
            if listings:
                self.logger.info(f"Successfully scraped {len(listings)} office building listings")
                
                # Store summary in memory
                summary = f"Property scraping completed: Found {len(listings)} office buildings in Nanjing over 5 million RMB"
                self.assistant.store_learning(
                    learning=summary,
                    source="property_scraping_task",
                    tags=["property_scraping", "summary", "nj"]
                )
                
                # Save detailed data to file
                if self.assistant.data_scraper:
                    await self.assistant.data_scraper.save_scraped_data(
                        listings, 
                        f"nj_office_buildings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )
            else:
                self.logger.info("No listings found or scraping failed")
                
                # Store failure notice
                self.assistant.store_learning(
                    learning="Property scraping task completed but found no listings meeting criteria",
                    source="property_scraping_task",
                    tags=["property_scraping", "failure", "no_results"]
                )
                
        except Exception as e:
            self.logger.error(f"Error in property scraping task: {str(e)}")
            # Store error in memory
            self.assistant.store_learning(
                learning=f"Property scraping task failed with error: {str(e)}",
                source="property_scraping_task",
                tags=["property_scraping", "error", "exception"]
            )
        finally:
            self.is_running = False
            self.logger.info("Property scraping task completed")
            
    async def run_with_retry(self, max_retries: int = 3):
        """Run the task with retry logic"""
        for attempt in range(max_retries):
            try:
                await self.run()
                return  # Success, exit retry loop
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in 30 seconds...")
                    await asyncio.sleep(30)  # Wait before retry
                else:
                    self.logger.error("All retry attempts failed")
                    # Store final failure in memory
                    self.assistant.store_learning(
                        learning=f"Property scraping task failed after {max_retries} attempts: {str(e)}",
                        source="property_scraping_task",
                        tags=["property_scraping", "retry_failure", "permanent_error"]
                    )