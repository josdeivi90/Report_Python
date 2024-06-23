import getopt
import sys
import os

from datetime import datetime, timezone
from utils.configuration import load_configuration
from utils.json_file_da import write_to_json
from loaders.harnessloader import load_perspective_costs

def do_audit():
    # Obtiene la fecha y hora actual en UTC
    current_month = int(datetime.now(timezone.utc).strftime('%m'))
    current_year = int(datetime.now(timezone.utc).strftime('%y')) + 2000
    current_day = int(datetime.now(timezone.utc).strftime('%d'))

    # Obtiene los argumentos de la línea de comandos, excluyendo el nombre del script
    argv = sys.argv[1:]
    METRIC_MONTH = current_month
    METRIC_YEAR = current_year

    try:
        # Analiza los argumentos de la línea de comandos
        opts, args = getopt.getopt(argv, "m:y:c", ['month=', 'year='])
    except getopt.GetoptError:
        # Muestra el uso correcto del script si hay un error en los argumentos
        print('monthly_metrics.py -m <month> -y <year>')
        sys.exit(2)

    # Asigna los argumentos a variables según la opción
    for opt, arg in opts:
        if opt == '-h':
            print('monthly_metrics.py -m <month> -y <year>')
            sys.exit()
        elif opt in ("-m", "--month"):
            METRIC_MONTH = int(arg)
        elif opt in ("-y", "--year"):
            METRIC_YEAR = int(arg)

    # Función para calcular el total de costos por perspectivas
    def total_perspectives(data):
        total = 0
        for perspective in data:
            print(perspective["application"] + ": " + str(perspective["total"]))
            total += perspective["total"]
        print("------------------")
        print("total" + ": " + str(total))
        return total

    # Carga la configuración desde un archivo JSON
    config = load_configuration("./config/audit_config.json")

    # Carga datos de costos de aplicaciones de Harness
    print("...Loading Harness App Perspectives...")
    harness_token = os.environ['HARNESS_API_TOKEN']
    if METRIC_MONTH != current_month:
        current_day = 0
    app_cost_data = load_perspective_costs(harness_token, config["harness_application_costs"][0], METRIC_MONTH, METRIC_YEAR, current_day)

    # Carga datos de costos de servicios de Harness
    print("...Loading Harness Service Perspectives...")
    if METRIC_MONTH != current_month:
        current_day = 0
    service_cost_data = load_perspective_costs(harness_token, config["harness_service_costs"][0], METRIC_MONTH, METRIC_YEAR, current_day)

    # Calcula el total de costos para aplicaciones y servicios
    app_total = total_perspectives(app_cost_data)
    service_total = total_perspectives(service_cost_data)

    # Crea un diccionario con los totales de costos
    thisdata = {
        "app_total": app_total,
        "service_total": service_total
    }
    return thisdata

def main():
    # Llama a la función de auditoría y obtiene los datos de costos
    data = do_audit()
    app_total = data["app_total"]
    service_total = data["service_total"]
    error_total = (service_total - app_total)

    # Imprime los totales y el error
    print("application total: " + str(app_total))
    print("service total: " + str(service_total))
    print("missing total: " + str(error_total))
    print("percent error: " + str((error_total / app_total) * 100) + "%")

    # Crea un diccionario con los datos de la auditoría
    data = {
        "data": {
            "cost_audit": {
                "app_total": app_total,
                "service_total": service_total,
                "error_total": error_total,
                "percent_error": (error_total / app_total) * 100
            }
        }
    }

    # Escribe los datos de la auditoría a un archivo JSON
    write_to_json('./data/audit_data.json', data)

# Llama a la función main si el script se ejecuta directamente
if __name__ == "__main__":
    main()
