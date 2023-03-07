# Bar Chart Race of Singapore's HDB Resale Prices per District

## Prerequisites

-   Python 3.6+
-   [pnpm](https://pnpm.io/installation)
-   [Node.js](https://nodejs.org/en/)

If you are on Linux/MacOS, you can install pnpm using the following command:

```bash
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

## Step 1: Prepare Data for Bar Chart Race

```bash
python3 python/prepare_race_data.py
```

## Step 2: Run Bar Chart Race

```bash
cd bar-chart-race
```

Install dependencies

```bash
pnpm install
```

Run development server

```bash
pnpm run dev
```

Build static website

```bash
cd bar-chart-race
pnpm run build
```

Now, you can find the static website in the `dist` folder.
