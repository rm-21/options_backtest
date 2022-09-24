**Exercise**

1. Write a Function to get ATM Strike given Date & Time

2. Write a Function to get Strike (CE & PE) which is closest to a Premium of 100 at a given Date/Time/Expiry

3. Backtest the SET Strategy for a period of 9 months [202104 to 202112] <br><br>

**Strategy Rules**

- On the day of Expiry, Select Strikes (Call & Put) trading at a premium nearest to 100 at 0930hrs [Lets say the Strikes are CE1 & PE1 with premiums being C1 & P1]
-  Entry: Short Triggered if CE1 hits C1/2. Short Trigerred if PE1 hits P1/2
- SL for CE1 @ C1 & SL for PE2 @ P1
- Exit at 1520hrs if SL not hit

Output: Date, Expiry, Instrument, Entry, Entry Time, SL, Exit, Exit Time 
