# Exploratory Data Analysis of Cryptocurrency Posts and Comments

This notebook provides an exploratory analysis of a dataset containing posts and comments related to cryptocurrencies. The goal is to understand trends, activity across different cryptocurrencies, and text characteristics.

## What We Did

1. **Identify posts and comments**  
   - Using the `unified_id` column, we classified each entry as either a post or a comment.

2. **Analyze daily activity**  
   - Extracted dates from the dataset and computed the number of posts, comments, and total entries per day.  
   - Visualized the **daily evolution** to see trends over time.

3. **Cryptocurrency analysis**  
   - Extracted cryptocurrencies mentioned in the `subreddit` column.  
   - Calculated the number of posts and comments for each crypto.  
   - Plotted the **distribution of activity** for the top cryptocurrencies and highlighted the **most mentioned cryptos**.

4. **Text length analysis**  
   - Measured the length of each post and comment.  
   - Computed basic statistics (minimum, maximum, average, variance) to understand the content size.

5. **Visualization and logging**  
   - Used **charts** to make trends and distributions visible.  
   - Logged key results instead of printing, keeping the notebook clean and easy to follow.

## Outcome

- Clear view of activity over time (posts vs comments).  
- Identification of the most active and most mentioned cryptocurrencies.  
- Understanding of content length and variability.  
- Visual charts that summarize the main patterns in the dataset.

## How to Use

1. Place the dataset `master_dataset.csv`.  
2. Open the notebook and run the cells sequentially to reproduce the analysis and charts.
