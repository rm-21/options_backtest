# Options Backtesting

## Index Data Sanity Check

### Data Info


 

    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 69374 entries, 2021-04-01 09:15:00 to 2021-12-30 15:29:00
    Data columns (total 8 columns):
     #   Column      Non-Null Count  Dtype         
    ---  ------      --------------  -----         
     0   ticker      69374 non-null  object        
     1   open        69374 non-null  float64       
     2   high        69374 non-null  float64       
     3   low         69374 non-null  float64       
     4   close       69374 non-null  float64       
     5   atm_strike  69374 non-null  int64         
     6   spread      69374 non-null  object        
     7   expiry      69374 non-null  datetime64[ns]
    dtypes: datetime64[ns](1), float64(4), int64(1), object(2)
    memory usage: 4.8+ MB


### Close


 


    
![png](output_10_0.png)
    


No sudden spikes or falls in the close price of the index.

### Standard Deviation


 


    
![png](output_13_0.png)
    


Standard Deviation is in a well-defined range

## Strategy

### Run Strategy
The function will take time to run since it is event-based backtesting. It is recommended to load `trade_book.csv` for analysis.
strategy.run_strategy()
### Analysis
The analysis is not considering any costs of execution for now. Slippage equal to 3% on the negative side is being assumed to take a conservative view.


 




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>instrument</th>
      <th>datetime</th>
      <th>points</th>
      <th>position_type</th>
      <th>expiry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>BANKNIFTY2140133700CE</td>
      <td>2021-04-01 10:48:00</td>
      <td>41.81</td>
      <td>Entry</td>
      <td>2021-04-01 15:30:00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>BANKNIFTY2140133100PE</td>
      <td>2021-04-01 13:05:00</td>
      <td>40.30</td>
      <td>Entry</td>
      <td>2021-04-01 15:30:00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>BANKNIFTY2140133700CE</td>
      <td>2021-04-01 14:10:00</td>
      <td>-98.52</td>
      <td>SL</td>
      <td>2021-04-01 15:30:00</td>
    </tr>
    <tr>
      <th>3</th>
      <td>BANKNIFTY2140133100PE</td>
      <td>2021-04-01 15:20:00</td>
      <td>-0.26</td>
      <td>Time</td>
      <td>2021-04-01 15:30:00</td>
    </tr>
    <tr>
      <th>4</th>
      <td>BANKNIFTY2140833500CE</td>
      <td>2021-04-08 09:51:00</td>
      <td>43.26</td>
      <td>Entry</td>
      <td>2021-04-08 15:30:00</td>
    </tr>
  </tbody>
</table>
</div>



#### PnL


 


    
![png](output_21_0.png)
    


    
    Period: 2021-04-01 to 2021-12-30
    
    Net points  : 711.25
    Gross Gained: 1259.05
    Gross Lost  : 547.8
    Weekly Avg. : 17.78
    
    Max. Gained : 95.8 on 2021-04-15
    Max. Lost   : 132.49 on 2021-11-25
    
    Number of Expiries Traded    : 40
    Number of Profitable Expiries: 24
    Number of Loss  Expiries     : 16
    Hit Ratio                    : 60.0%
    



 


    
![png](output_22_0.png)
    


The returns are more concentrated on the right. There is a possibility of a big loss, but it is fairly low.

#### Trades
- Time refelects exit of the positions at a specific time
- SL refelcts exit by Stop Loss hit


 


    
![png](output_25_0.png)
    


Almost 72% of the time we exited because of a hard time stop. Rest 18% of the time SL was hit. We could experiment with lowering the SL.

#### Expiries where SL was Hit


 


    
![png](output_28_0.png)
    


There is clearly a systematic pattern to losses. By a simple visual analysis, it is evident that after every 3/4 successive profits, there are 2/3 successive losses. A deep dive can be conducted to find the cyclical nature or the market and take a decision on whether or not to actually trade.

#### Most Common Hours for Entry/Exit
`Blue is Entry | Orange is Exit`


 


    
![png](output_31_0.png)
    


Maximum entries happen in the first 2 hours of the market. Maximum exits happen at close. It would be curious to see that the few exits that happen between 10 and 13 hours are SLs or not. If they are, they could reveal some insights about the market structure that can be leveraged.
