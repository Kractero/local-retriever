import requests
import time
import xmltodict
import argparse
import config
from pathlib import Path

def sleep(seconds):
    time.sleep(seconds)

def main():
    parser = argparse.ArgumentParser(description='Process deck data')
    parser.add_argument('-e', '--elevated', action='store_true', help='Gets packs and issues')

    args = parser.parse_args()

    with open('puppets_list.txt', 'r') as file:
        nation_list = file.read().splitlines()

    if not nation_list:
        raise ValueError("No puppet list.")

    deck_data = []
    headers = {
        'User-Agent': config.user_agent
    }

    if not headers['User-Agent']:
        raise ValueError("User-Agent value is missing or empty.")

    if args.elevated:
        headers['X-Password'] = config.password
        if not headers['X-Password']:
            raise ValueError("X-Password value is missing or empty.")

    for entry in nation_list:
        deck_url = f'https://www.nationstates.net/cgi-bin/api.cgi?q=cards+deck;nationname={entry}'
        response = requests.get(deck_url, headers=headers)
        deck_data_xml = xmltodict.parse(response.text)
        category_counts = {}

        if 'CARDS' in deck_data_xml:
            if 'DECK' in deck_data_xml['CARDS'] and deck_data_xml['CARDS']['DECK'] is not None:
                deck = deck_data_xml['CARDS']['DECK']['CARD']
                for card in deck:
                    category = card['CATEGORY']
                    category_counts[category] = category_counts.get(category, 0) + 1

        junk_value = (
            (category_counts.get('legendary', 0) * 1) +
            (category_counts.get('epic', 0) * 0.5) +
            (category_counts.get('common', 0) * 0.01) +
            (category_counts.get('uncommon', 0) * 0.05) +
            (category_counts.get('ultra-rare', 0) * 0.2)
        )

        sleep (0.7)

        owner_info_url = f'https://www.nationstates.net/cgi-bin/api.cgi?q=cards+info;nationname={entry}'
        response = requests.get(owner_info_url, headers=headers)
        deck_owner_info_xml = xmltodict.parse(response.text)
        deck_info = deck_owner_info_xml.get('CARDS', {}).get('INFO', {})

        data = {
            'nation': entry,
            'bank': deck_info.get('BANK', 0),
            'deckValue': deck_info.get('DECK_VALUE', 0),
            'junkValue': junk_value
        }

        sleep(0.7)

        if args.elevated:
            pack_and_issues_url = f'https://www.nationstates.net/cgi-bin/api.cgi?nation={entry}&q=issues+packs'
            response = requests.get(pack_and_issues_url, headers=headers)
            pack_and_issues_xml = xmltodict.parse(response.text)
            packs = pack_and_issues_xml.get('NATION', {}).get('PACKS', 0)
            issues_array = pack_and_issues_xml.get('NATION', {}).get('ISSUES', {}).get('ISSUE', [])
            number_of_issues = len(issues_array)

            data['packs'] = packs
            data['issues'] = number_of_issues

            sleep(0.7)

        deck_data.append(data)

    with open('local_retriever.html', 'w') as output_file:
        output_file.write('''
            <html>
                <head>
                    <style>
                        body {
                            font-size: 14px;
                            font-family: Arial, sans-serif;
                            color: #6b7280;
                        }

                        table {
                            width: 100%;
                            caption-side: bottom;
                            font-size: 14px;
                            text-align: left;
                            border-collapse: collapse;
                        }

                        table caption {
                            margin-top: 1rem;
                            font-size: 14px;
                            color: #6b7280;
                        }

                        table thead tr {
                            border-bottom: 1px solid;
                        }

                        table th {
                            height: 48px;
                            padding: 0 16px;
                            font-weight: 500;
                            color: #6b7280;
                        }

                        table td {
                            padding: 16px;
                        }

                        table tbody tr {
                            border-bottom: 1px solid;
                        }

                        a {
                            text-decoration: none;
                        }

                        a:hover {
                            text-decoration: underline;
                        }
                    </style>
                </head>
            <body>
                <table>
        ''')
        output_file.write("<tr><th>Nation</th><th class='sort' data-order='none'>Bank</th><th class='sort' data-order='none'>Deck Value</th><th class='sort' data-order='none'>Junk Value</th>")
        if args.elevated:
            output_file.write("<th class='sort' data-order='none'>Packs</th><th class='sort' data-order='none'>Issues</th>")
        output_file.write("</tr>\n")

        for entry in deck_data:
            output_file.write(f"<tr><td><a target='_blank' href='https://www.nationstates.net/container={entry['nation']}/nation={entry['nation']}'>{entry['nation']}</a></td><td><a target='_blank' href='https://www.nationstates.net/page=deck/container={entry['nation']}/nation={entry['nation']}/value_deck=1'>{entry['bank']}</a></td><td><a target='_blank' href='https://www.nationstates.net/page=deck/container={entry['nation']}/nation={entry['nation']}/value_deck=1'>{entry['deckValue']}</a></td><td><a target='_blank' href='https://www.nationstates.net/page=deck/container={entry['nation']}/nation={entry['nation']}'>{entry['junkValue']}</a></td>")
            if args.elevated:
                output_file.write(f"<td><a target='_blank' href='https://www.nationstates.net/page=deck/container={entry['nation']}/nation={entry['nation']}'>{entry['packs']}</a></td><td><a target='_blank' href='https://www.nationstates.net/container={entry['nation']}/nation={entry['nation']}'>{entry['issues']}</a></td>")
            output_file.write("</tr>\n")

        output_file.write("</table>\n")

        output_file.write('''
                <script>
                    document.querySelectorAll("a").forEach(function (el) {
                        el.addEventListener("click", function () {
                            let myidx = 0;
                            const row = el.parentNode.parentNode;
                            let child = el;
                            while ((child = child.previousElementSibling) != null) {
                                myidx++;
                            }
                            row.nextElementSibling.childNodes[myidx].querySelector("a").focus();
                            row.parentNode.removeChild(row);
                        });
                    });
                    const sortableColumns = document.querySelectorAll('.sort');
                    sortableColumns.forEach(col => {
                        col.addEventListener('click', () => {
                            const table = document.querySelector('table');
                            const columnIndex = Array.from(col.parentNode.cells).indexOf(col);

                            const rows = Array.from(table.rows).slice(1);
                            const isNumeric = columnIndex >= 1 && columnIndex <= 4;
                            const currentOrder = col.getAttribute('data-order');
                            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
                            rows.sort((a, b) => {
                                const aValue = isNumeric ? parseFloat(a.cells[columnIndex].innerText) : a.cells[columnIndex].innerText;
                                const bValue = isNumeric ? parseFloat(b.cells[columnIndex].innerText) : b.cells[columnIndex].innerText;
                                if (currentOrder === 'asc' && currentOrder !== 'none') {
                                    return aValue > bValue ? 1 : aValue === bValue ? 0 : -1;
                                } else {
                                    return aValue > bValue ? -1 : aValue === bValue ? 0 : 1;
                                }
                                return aValue > bValue ? 1 : aValue === bValue ? 0 : -1;;
                            });
                            table.tBodies[0].append(...rows);
                            col.setAttribute('data-order', newOrder);
                        });
                    });
                </script>
            </body>
            </html>
        ''')

if __name__ == "__main__":
    main()