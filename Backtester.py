import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")


class Backtester():
    
    def __init__(self, dfn, prices, margins):
        self.dfn = dfn
        self.prices = prices
        self.margins = margins
    
    def execute_trades(self,datetime, i, capital, signal, position, qty, equity, trade_type, entry, exit, entry_price, exit_price):
        
        if i== 0:
            equity.append(capital)
            datetime.append(self.dfn.index[i])
        
        # If there is no position, carry the existing equity
        if position == 0 and i > 0:
            datetime.append(self.dfn.index[i])
            equity.append(equity[-1])

        # If there is an open position carry the position and the entry price

        if position != 0:
            todays_pnl = qty[-1]*position*(self.prices.iloc[i] - self.prices.iloc[i-1])
            eq = equity[-1] + todays_pnl
            datetime.append(self.dfn.index[i])
            equity.append(eq)

        # Entry long

        if signal == 'Long' and position == 0:
            position = 1
            trade_value = equity[-1]
            margin = self.margins.iloc[i]
            qty.append(round(trade_value / margin, 0))
            #print(i, self.dfn.index[i], self.prices.iloc[i])
            entry.append(self.dfn.index[i])
            entry_price.append(self.prices.iloc[i])
            trade_type.append('Long')

        # Check take profit and stop loss for long position  

        elif position == 1 and (signal == 'Long Square Off' or i == len(self.dfn) -1):

            position = 0
            exit.append(self.dfn.index[i])
            exit_price.append(self.prices.iloc[i])
            
         # Entry Short

        if signal == 'Short' and position == 0:
            position = -1
            trade_value = equity[-1]
            margin = self.margins.iloc[i]
            qty.append(round(trade_value / margin, 0))
            entry.append(self.dfn.index[i])
            entry_price.append(self.prices.iloc[i])
            trade_type.append('Short')

        # Check take profit and stop loss for short position  

        elif position == -1 and signal == 'Short Square Off':

            position = 0
            exit.append(self.dfn.index[i])
            exit_price.append(self.prices.iloc[i])
            
        if i == len(self.dfn) -1 and position !=0:
            position = 0
            exit.append(self.dfn.index[i])
            exit_price.append(self.prices.iloc[i])
            
        return position, qty, equity, datetime, trade_type, entry, exit, entry_price, exit_price    
    
    def create_trade_log(self, qty, trade_type, entry, exit, entry_price, exit_price):
        trade_log = pd.DataFrame()
        trade_log['Entry Date'] = entry
        trade_log['Entry Price'] = entry_price
        trade_log['Quantity'] = qty
        trade_log['Exit Date'] = exit
        trade_log['Exit Price'] = exit_price
        trade_log['Trade Type'] = trade_type
        
        return trade_log
    
    def calculate_accuracy(self, trade_log):
        
        long_wins, long_loss, short_wins, short_loss = 0,0,0,0
        accuracy, long_accuracy, short_accuracy = 0,0,0

        for i in range(len(trade_log)):

            if trade_log['Trade Type'].iloc[i] == 'Long':
                if trade_log['Exit Price'].iloc[i] > trade_log['Entry Price'].iloc[i]:
                    long_wins += 1
                else:
                    long_loss += 1

            if trade_log['Trade Type'].iloc[i] == 'Short':
                if trade_log['Exit Price'].iloc[i] < trade_log['Entry Price'].iloc[i]:
                    short_wins += 1
                else:
                    short_loss += 1
                    
        accuracy = (long_wins + short_wins) / (long_wins + short_wins + long_loss + short_loss)
        
        if (long_wins + long_loss) != 0:
            long_accuracy = long_wins / (long_wins + long_loss)
            
        if short_wins + short_loss !=0:
            short_accuracy = short_wins / (short_wins + short_loss)
        
        return accuracy, long_accuracy, short_accuracy
    
    def calculate_backtest_results(self, datetime, equity):
        
        account = pd.DataFrame()
        account['Datetime'] = datetime
        account['Equity'] = equity
        
        account['Returns'] = account['Equity'].pct_change()

        stra_cagr = (equity[-1]/equity[0])**(365.25/((datetime[-1]-datetime[0]).days)) -1

        Roll_Max = account['Equity'].cummax()
        Daily_Drawdown = account['Equity']/Roll_Max -1
        Max_Daily_Drawdown = Daily_Drawdown.cummin()
        stra_mdd = round(Max_Daily_Drawdown.iloc[-1],3)

        strategy_sharp = ((account['Returns'].mean())*252 - 0.05)/(account['Returns'].std()*np.sqrt(252))

        strategy_sortino = ((account['Returns'].mean())*252 - 0.05)/((account['Returns']<1).std()*np.sqrt(252))
        
        strategy_calmar = round(-1*stra_cagr/stra_mdd, 1)

        #winners = list(filter(lambda x:x>0, pnl))
        #avg_win = sum(winners)*100/len(winners)

        headers = ['Strategy']
        row = ['CAGR', 'MAX DD', 'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio']
        backtest = [stra_cagr, stra_mdd, strategy_sharp, strategy_sortino, strategy_calmar]


        account.plot(x='Datetime', y=['Equity'], figsize=(20,12))

        results = pd.DataFrame(backtest, row, headers)
        return account, results
