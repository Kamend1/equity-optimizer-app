from EquityOptimizerApp.equity_optimizer.services import stock_service, stock_data_service

tickers = [
    "ABT", "ACN", "ADBE", "ADI", "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AFL", "AIG", "AIV", "AJX", "AKAM",
    "ALB", "ALGN", "ALK", "ALL", "ALLE", "ALLY", "AMAT", "AMD", "AME", "AMGN", "AMT", "AMZN", "ANSS", "AON",
    "AOS", "APA", "APD", "APH", "APTV", "ARE", "ARL", "ATO", "AVB", "AVGO", "AVY", "AWK", "AXP", "AZO", "BA",
    "BAC", "BAX", "BBY", "BCE", "BDX", "BEAM", "BEN", "BIIB", "BK", "BKNG", "BKR", "BLK", "BMY", "BR", "BSX",
    "BTG", "BWA", "BXP", "C", "CAG", "CAH", "CARR", "CART", "CAT", "CBRE", "CCI", "CCL", "CDNS", "CE", "CHD",
    "CHK", "CHKP", "CHRW", "CI", "CINF", "CL", "CLF", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF",
    "COO", "COP", "COST", "CPB", "CRM", "CSCO", "CSX", "CTAS", "CTSH", "CVS", "CVX", "D", "DAL", "DD", "DE",
    "DFS", "DG", "DGX", "DHI", "DHR", "DIS", "DLR", "DLTR", "DOV", "DOW", "DPZ", "DRI", "DTE", "DTG.DE", "DUK",
    "DVA", "DVN", "DXC", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EIX", "EL", "EMR", "ENB", "ES", "ESS",
    "ETR", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FAST", "FCX", "FDX", "FE", "FFIV", "FIS", "FITB",
    "FLS", "FMC", "FND", "FRE.DE", "FRT", "GE", "GILD", "GIS", "GLW", "GM", "GOOG", "GOOGL", "GPC", "GPN",
    "GPS", "GRMN", "GS", "GT", "GWW", "HAL", "HAS", "HBAN", "HBI", "HCA", "HCP", "HD", "HES", "HIG", "HII",
    "HLT", "HMC", "HNR1.DE", "HON", "HPE", "HPI", "HPQ", "HRB", "HRL", "HSIC", "HST", "HSY", "HUM", "IBM",
    "ICE", "IDXX", "IFF", "ILMN", "INCY", "INTC", "INTU", "IP", "IPG", "IPGP", "IQV", "IRM", "JCI", "JNJ",
    "JPM", "JWN", "K", "KEY", "KEYS", "KHC", "KIM", "KLAC", "KMI", "KMX", "KO", "KR", "KSS", "L", "LB", "LEG",
    "LEN", "LH", "LHX", "LIN", "LKQ", "LLY", "LMT", "LNC", "LOW", "LRCX", "LULU", "LUV", "LVS", "LYB", "LYV",
    "MA", "MAA", "MAC", "MAR", "MAS", "MAT", "MCD", "MCHP", "MCK", "MDLZ", "MDT", "MET", "META", "MGM", "MHK",
    "MKC", "MLM", "MMC", "MMM", "MNST", "MO", "MOS", "MPC", "MRK", "MRNA", "MSCI", "MSFT", "MSI", "MTB", "MTD",
    "MU", "NDAQ", "NEE", "NEM", "NFLX", "NKE", "NOC", "NOW", "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVDA",
    "NVR", "NWS", "NWSA", "O", "OKE", "OMC", "ORCL", "ORLY", "OXY", "PAYX", "PCAR", "PCG", "PEG", "PEP", "PFE",
    "PG", "PH", "PHM", "PKG", "PLD", "PM", "PNC", "PNR", "PNW", "PPG", "PPL", "PRGO", "PRU", "PSA", "PSX",
    "PVH", "PWR", "PYPL", "QCOM", "QRVO", "RCL", "REGN", "REGX", "RF", "RHI", "RJF", "RL", "RMD", "ROK", "ROL",
    "ROP", "ROST", "RS", "RTX", "RYAAY", "S", "SBAC", "SBUX", "SCHW", "SEE", "SHL.DE", "SHW", "SLB", "SLG",
    "SNA", "SNAP", "SO", "SPG", "SPGI", "SRE", "SRG", "STT", "STX", "STZ", "SU.PA", "SYK", "SYY", "T", "TAP",
    "TDG", "TEL", "TER", "TFC", "TFX", "TGT", "TJX", "TMO", "TNC", "TROW", "TRV", "TSLA", "TTWO", "TXN", "TXT",
    "UAL", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI", "USB", "V", "VFC", "VLO", "VMC", "VNO", "VNT",
    "VRTX", "VTR", "VZ", "WAB", "WAT", "WBA", "WDC", "WEC", "WFC", "WHR", "WING", "WM", "WMB", "WMT", "WRK",
    "WSM", "WST", "XEL", "XOM", "XRAY", "XRX", "XYL", "YUM", "ZBH", "ZBRA"
]

for ticker in tickers:
    print(f'Processing ticker: {ticker}')
    if stock_service.check_stock_exists(ticker):
        print(f'Stock {ticker} already exists. Skipping.')
        continue
    try:
        stock = stock_service.add_stock_to_db(ticker)
        stock_list = [stock]
        stock_data_service.download_and_save_stock_data(stock_list)
        print(f'Successfully added stock: {ticker}')
    except Exception as e:
        print(f'Error adding stock {ticker}: {str(e)}')