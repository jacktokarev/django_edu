import csv
from django.db.models import QuerySet
from django.db.models.options import Options
from django.http import HttpRequest, HttpResponse
from django.db.models.fields.related import ForeignKey
from django.urls import path
from django.shortcuts import render, redirect
from .forms import CSVImportForm, CSVImportManyForm
from .common import save_csv_items, save_related_csv_items

class ExportAsCSVMixin:
    
    def export_csv(self, request: HttpRequest, queryset: QuerySet):
        
        meta: Options = self.model._meta
        field_names = [f"{field.name}_id" if type(field) is ForeignKey else field.name for field in meta.fields]
        related_field_names = [f"{field.name}_ids" for field in meta.many_to_many]
        
        cls_name = self.model.__name__.lower()
        
        response = HttpResponse(content_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={cls_name}-export.csv"
        
        csv_writer = csv.writer(response)
        csv_writer.writerow(field_names + related_field_names)

        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            rel_fields = [",".join([','.join(str(inst.id) for inst in getattr(obj, field.split("_ids")[0]).all())]) for field in related_field_names]
            row.extend(rel_fields)         
            csv_writer.writerow(row)
        
        return response
    export_csv.short_description = "Export as CSV"


# class ExportRelatedAsCSVMixin:

#     def export_related_csv(self, request: HttpRequest, queryset: QuerySet):
#         meta: Options = self.model._meta
#         field_names = [field.name for field in meta.many_to_many]
#         cls_name = self.model.__name__.lower()
        
#         response = HttpResponse(content_type="text/csv")
#         response.headers["Content-Disposition"] = f"attachment; filename={cls_name}-related-export.csv"
        
#         csv_writer = csv.writer(response)
#         csv_writer.writerow([f"{cls_name}_id", "field_name", "related_id"])
        
#         for inst in queryset:
#             for field_name in field_names:
#                 items = getattr(inst, field_name).all()
#                 for r_inst in items:
#                     csv_writer.writerow([inst.id, field_name, r_inst.id])
#         return response
#     export_related_csv.short_description = "Export related as CSV"


class ImportCSVMixin:
    """This mixin should be the first on the list of parents"""

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)
        save_csv_items(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
            model_type=self.model
        )
        self.message_user(request, "Date from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [get_path(self.model, "import", "csv", self.import_csv),]
        return new_urls + urls

class ImportManyCSVMixin:
    """This mixin should be the first on the list of parents"""

    def import_related_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportManyForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_many_form.html", context)
        form = CSVImportManyForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_many_form.html", context, status=400)
        save_related_csv_items(
            file=form.files['csv_file'].file,
            # rel_file=form.files['csv_related_file'].file,
            encoding=request.encoding,
            model_type=self.model
        )
        self.message_user(request, f"Date from CSV in was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [get_path(self.model, "import", "relcsv", self.import_related_csv)]
        return new_urls + urls


def get_path(model, prefix, suffix, view):
    name = model.__name__.lower()
    return path(
        f"{prefix}-{name}-{suffix}/",
        view=view,
        name=f"{prefix}_{name}_{suffix}",
    )
