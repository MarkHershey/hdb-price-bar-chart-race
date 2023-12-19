# Singapore HDB Resale Price Bar Chart Race

## Overview

This project is an animated visualization that showcases how Singapore's public housing (HDB) flat prices have changed over the years (2012 - present) per town. The visualization takes the form of a bar chart race, which is a dynamic chart that displays the ranking of values over time.

Data source: [HDB Resale Flat Prices](https://beta.data.gov.sg/collections/189/view)

## Development

Powered by [Vite](https://vitejs.dev/) and [D3.js](https://d3js.org/).

### Prerequisites

-   [Python 3.6+](https://www.python.org/)
-   [Node.js](https://nodejs.org/)
-   [pnpm](https://pnpm.io/installation)

If you are on Linux/MacOS, you can install pnpm using the following command:

```bash
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

### Step 1: Prepare Data for Bar Chart Race

```bash
python3 python/prepare_race_data.py
```

### Step 2: Run Bar Chart Race

Install dependencies

```bash
cd bar-chart-race
pnpm install
```

Run development server

```bash
pnpm run dev
```

### Deployment

Build static files

```bash
cd bar-chart-race
pnpm run build
```

Now, you can find the static website in the `dist` folder.

## References

-   [Bar Chart Race, Explained](https://observablehq.com/@d3/bar-chart-race-explained) by [Mike Bostock](https://observablehq.com/@mbostock)
