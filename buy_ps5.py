import sites as s
from multiprocessing import Process
import argparse
import json

all_sites = {
    'costco': s.Costco,
    'walmart': s.Walmart,
    'bestbuy': s.Bestbuy
}

def run_site(site_name: str, product: str):
    all_sites[site_name]('./chromedriver', './credentials.json').launch(product)

def main():

    parser = argparse.ArgumentParser(description='Get path to config file.')
    parser.add_argument('--config', type=str)

    args = parser.parse_args()

    print(args.config)

    configuration = json.load(open(args.config))

    processes = []

    for site, products in configuration.items():
        for product in products.values():
            prod = product if product != 'N/A' else None
            p = Process(target=run_site, args=(site, prod))
            p.start()
            processes.append(p)

    for p in processes:
        p.join()


if __name__ == '__main__':
    main()