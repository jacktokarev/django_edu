from io import TextIOWrapper
from csv import DictReader

def save_csv_items(file, encoding, model_type):
    reader = get_reader(file=file, encoding=encoding)
    model_items = [
        model_type(**row) for row in reader
    ]
    model_type.objects.bulk_create(model_items)
    return model_items

def save_related_csv_items(file, encoding, model_type):
    reader = get_reader(file = file, encoding=encoding)

    many_fields_rows = []
    model_items = []
    for row in reader:
        fields = {}
        many_fields = {}
        for key, value in row.items():
            if key[-4:] == "_ids":
                many_fields[key[:-4]] = value
            else:
                fields[key] = value
        many_fields_rows.append(many_fields)
        model_items.append(model_type(**fields))
    model_items = model_type.objects.bulk_create(model_items)
    for inst in model_items:
        for key, values in many_fields_rows.pop(0).items():
            getattr(inst, key).set(values.split(","))
    return model_items
            

def get_reader(file, encoding):
    csv_file = TextIOWrapper(
        buffer=file,
        encoding=encoding
    )
    return DictReader(csv_file)

def get_model_item(model_items, pk):
    for model in model_items:
        if model.pk == pk:
            return model


