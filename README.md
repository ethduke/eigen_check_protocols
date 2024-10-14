# Eigen Protocol Airdrop Checker

- Checks addresses against multiple airdrop APIs:
  - Puffer Finance
  - EtherFi
  - Eigen Foundation (Season 2)
  - Renzo Protocol

## Installation

1. Clone the repository:
   \`\`\`
   git clone https://github.com/ethduke/eigen_check_protocols.git
   cd eigen-airdrop-checker
   \`\`\`

2. Install the required packages:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

## Configuration

1. Add your Ethereum addresses to check in the \`evm.txt\` file, one address per line.
2. (Optional) Add proxy servers to \`proxies.txt\`, one proxy per line in the format \`http://ip:port\` or \`https://ip:port\`.
3. Adjust the \`APIConfig\` in \`config.py\` if needed to modify API endpoints or headers.

## Usage

Run the main script:

\`\`\`
python main.py
\`\`\`

The script will process all addresses and output the results, showing which addresses are eligible for airdrops from different protocols.

## Output

The script will generate a \`results.json\` file containing the airdrop eligibility results for each address checked.