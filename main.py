import sys
import csv
from tabulate import tabulate

def where_csv(content: list, query: str) -> list:
    headers: list = content[0]
    if "=" in query:
        query_list = query.split("=")

        if len(query_list) != 2:
            raise ValueError("invalid where statement")

        query_header = query_list[0]

        if query_header not in headers:
            raise ValueError(f"there is no {query_header} in the csv file")
        else:
            index = headers.index(query_header)

        content = [headers] + [row for row in content[1:] if row[index] == query_list[1]]
    elif ">" in query:
        query_list = query.split(">")

        if len(query_list) != 2:
            raise ValueError("invalid where statement")

        query_header = query_list[0]

        if query_header not in headers:
            raise ValueError(f"there is no {query_header} in the csv file")
        else:
            index = headers.index(query_header)

        try:
            content = [headers] + [row for row in content[1:] if float(row[index]) > float(query_list[1])]
        except (ValueError, TypeError):
            raise ValueError("invalid value for where statement or incorrect csv file content")
    elif "<" in query:
        query_list = query.split("<")

        if len(query_list) != 2:
            raise ValueError("invalid where statement")

        query_header = query_list[0]

        if query_header not in headers:
            raise ValueError(f"there is no {query_header} in the csv file")
        else:
            index = headers.index(query_header)

        try:
            content = [headers] + [row for row in content[1:] if float(row[index]) < float(query_list[1])]
        except (ValueError, TypeError):
            raise ValueError("invalid value for where statement or incorrect csv file content")

    return content

def aggregate_csv(content: list, query: str) -> list:
    headers: list = content[0]
    if "=" in query:
        query_list = query.split("=")
        if len(query_list) != 2: raise ValueError("invalid aggregate statement")
    else:
        raise ValueError("invalid aggregate statement")

    query_header = query_list[0]
    if query_header not in headers:
        raise ValueError(f"there is no {query_header} in the csv file")
    else:
        index = headers.index(query_header)
    
    try:
        values = [float(row[index]) for row in content[1:]]
        if query_list[1] == "avg":
            content = [["avg"], [sum(values) / len(values)]]
        elif query_list[1] == "min":
            content = [["min"], [min(values)]]
        elif query_list[1] == "max":
            content = [["max"], [max(values)]]
    except (ValueError, TypeError):
        raise ValueError("incorrect csv file content for aggregation")
            
    return content

def processing_csv(path: str, *args, **kwargs):
    with open(path, newline='') as csv_file:
        content = list(csv.reader(csv_file, delimiter=',', quotechar='|'))

    if len(content) <= 0: 
        print("non-existent table")
    elif len(content) == 1: 
        print("empty table: \n", tabulate([], headers=content[0], tablefmt="grid"))

    try:
        if len(args) == 4 and args[0] == '--where' and isinstance(args[1], str) and args[2] == '--aggregate' and isinstance(args[3], str):
            content = aggregate_csv(where_csv(content, query=args[1]), args[3])
        elif len(args) == 2 and args[0] == '--where' and isinstance(args[1], str):
            content = where_csv(content, query=args[1])
        elif len(args) == 2 and args[0] == '--aggregate' and isinstance(args[1], str): 
            content = aggregate_csv(content, query=args[1])
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
    else:
        print(tabulate(content[1:], headers=content[0], tablefmt="grid"))

if __name__=="__main__":
    argvs = sys.argv
    if len(argvs) >= 3 and argvs[0] == "main.py" and argvs[1] == "--file" and argvs[2]:
        func_args = argvs[3:] if len(argvs) >= 4 else []
        processing_csv(argvs[2], *func_args)

