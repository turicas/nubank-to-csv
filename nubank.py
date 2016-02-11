#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import argparse
import datetime

from collections import OrderedDict
from decimal import Decimal
from re import compile as regexp_compile

import rows

from lxml.etree import HTML


REGEXP_PAGE = regexp_compile(r'^[0-9]+ de [0-9]+$')
MONTHS = 'JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ'
FIELDS = OrderedDict([('category', rows.fields.TextField),
                      ('description', rows.fields.TextField),
                      ('value', rows.fields.DecimalField),
                      ('date', rows.fields.DateField)])


def partition(data, number):
    for index in range(0, len(data), number):
        yield data[index:index + number]


def convert_text(text):
    return text.replace('\xa0', ' ')


def convert_value(value):
    return Decimal(convert_text(value).replace('.', '').replace(',', '.')
                                      .strip().replace(' ', ''))

def convert_date(value, year):
    day, month = convert_text(value).split()
    day = int(day)
    month = MONTHS.split().index(month) + 1
    return datetime.date(year, month, day)


def extract_month(entry):
    return convert_text(entry[3]).split()[1]


def html_to_table(input_filename, encoding='utf-8'):
    with open(input_filename) as fobj:
        html = fobj.read().decode(encoding).replace('\xa0', ' ')
    tree = HTML(html)

    data = tree.xpath('//body/b')
    for index, element in enumerate(data):
        text = element.text
        if text.startswith('Valores') and text.endswith('R$'):
            break
    new = []
    for element in data[index + 1:]:
        text = element.text
        if text.startswith('FATURA DE '):
            continue
        elif REGEXP_PAGE.findall(text):
            continue
        else:
            new.append(element.text)
    data = new

    chunks = list(partition(data, 4))
    table = rows.Table(fields=FIELDS)
    current_year = datetime.datetime.now().year
    months = set(extract_month(row) for row in chunks)
    subtract_year = 'DEZ' in months and 'JAN' in months
    for row in chunks:
        category = convert_text(row[0])
        description = convert_text(row[1])
        value = convert_value(row[2])
        year = current_year
        month = extract_month(row)
        if subtract_year and month in ('NOV', 'DEZ'):
            year = current_year - 1
        date = convert_date(row[3], year)
        table.append({'category': category,
                      'description': description,
                      'value': value,
                      'date': date, })

    return table


def sum_iof_into_entries(table):
    entries, iofs = [], {}
    for row in table:
        description = row.description.lower()
        if description.startswith('iof de "'):
            entry_description = description.split('"')[1].strip()
            iofs[entry_description] = row
        else:
            entries.append(row)

    table = rows.Table(fields=FIELDS)
    for entry in entries:
        description = entry.description.lower().strip()
        entry = {'description': entry.description.strip(),
                 'value': entry.value,
                 'category': entry.category,
                 'date': entry.date, }
        if description in iofs:
            iof = iofs[description]
            entry['description'] += ' (+ IOF)'
            entry['value'] += iof.value
        table.append(entry)

    table.order_by('date')
    return table


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('html_entrada')
    parser.add_argument('csv_saida')
    args = parser.parse_args()

    table = sum_iof_into_entries(html_to_table(args.html_entrada))
    rows.export_to_csv(table, args.csv_saida)


if __name__ == '__main__':
    main()
