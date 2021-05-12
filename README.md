# Assignment2(Trading Strategy)
Basic Thoughts
==
Richard proved with a simple set of systems and rules: through daily system training, person with little trading experience can be a good trader.

For this assignment, I would like to practice the turtle trading which is very basic trading strategy in algorithm trading system.

Turtle trading strategy is actually a trend trading strategy. The most prominent feature of it is to capture medium and long term trends. When showing the resonance throughout the market, this strategy can obtain the largest gains in the short term.

Trading Strategy
==
Stock
-
I select the representative stock——Sanqi Interactive Entertainment(601318). It has mid-term trend for these years.

Position
-
True range

![image](https://user-images.githubusercontent.com/80868998/118040635-61b21000-b3a4-11eb-8b59-454676df514b.png)

H is the highest price on that day; L is the lowest price; PDC is the close price on the day before. 

N can be calculated as the following equation.

![image](https://user-images.githubusercontent.com/80868998/118040916-c2414d00-b3a4-11eb-971d-bf03c6bff93b.png)

![image](https://user-images.githubusercontent.com/80868998/118040940-c9685b00-b3a4-11eb-813b-9b35711bd0cf.png)

Position Taking
==
System 1
-
Buy a Unit position if current prices are above the highest in the last 20 days.
Add Position: If the stock price rises 0.5N, then we buy one unit.

System 2
-
Change 20 days of System1 into 55.

Stop Loss
