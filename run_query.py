import query as qy
import argparse

def read_args():
    prefix = "+"
    ini_msg = "#"*120

    parser = argparse.ArgumentParser("Busqueda de picks o eventos. ",prefix_chars=prefix,
                        usage=f'Busqueda de picks o eventos.')

    parser.add_argument(prefix+"m",prefix*2+"mode",
                        type=str,
                        metavar='',
                        help="picks o events", required = True)

    parser.add_argument(prefix+"s",prefix*2+"start",
                        type=str,
                        metavar='',
                        help="Fecha inicial en formato 'yyyymmddThhmmss'", required = True)

    parser.add_argument(prefix+"e",prefix*2+"end",
                        type=str,
                        metavar='',
                        help="Fecha final en formato 'yyyymmddThhmmss'", required = True)

    parser.add_argument(prefix+"m_mag",prefix*2+"min_mag",
                        type=int,
                        metavar='',
                        help="Magnitud mínima", required = True)

    parser.add_argument(prefix+"M_mag",prefix*2+"max_mag",
                        type=int,
                        metavar='',
                        help="Magnitud máxima", required = True)
    
    parser.add_argument(prefix+"m_prof",prefix*2+"min_prof",
                        type=int,
                        metavar='',
                        help="Profundidad mínima", required = True)

    parser.add_argument(prefix+"M_prof",prefix*2+"max_prof",
                        type=int,
                        metavar='',
                        help="Profundidad máxima", required = True)
    
    parser.add_argument(prefix+"o",prefix*2+"out",
                        type=str,
                        default=None,
                        metavar='',
                        help=" csv format", required = True)

    parser.add_argument(prefix+"et",prefix*2+"event_type",
                        default=None,
                        nargs='+',
                        metavar='',
                        help="earthquake not_locatable explosion volcanic_eruption ... etc")

    parser.add_argument(prefix+"sta",prefix*2+"station_list",
                        default=None,
                        nargs='+',
                        metavar='',
                        help=" BAR2 RUS PTB")

    parser.add_argument(prefix+"id",prefix*2+"id",
                        default=None,
                        nargs='+',
                        metavar='',
                        help=" SGC2019xqwwuh SGC2019xpcvv")

    parser.add_argument(prefix+"r",prefix*2+"radial",
                        default=None,
                        nargs='+',
                        metavar='',
                        help="Se debe especificar: lat lon  r. Ejemplo: 6.81 -73.17 120")

    parser.add_argument(prefix+"mysqldb",prefix*2+"mysqldb",
                        default=None,
                        nargs='+',
                        metavar='',
                        help="Se debe especificar: host user passwd db. Ejemplo: 10.100.100.232 consulta consulta seiscomp3")
    


    args = parser.parse_args()
    args.start = args.start.replace("T"," ")
    args.end = args.end.replace("T"," ")
    # vars_args = vars(args)
    return args

if __name__ == "__main__":
    args = read_args()
    if args.mysqldb != None:
        MySQLdb_dict= {'host':args.mysqldb[0], 'user':args.mysqldb[1],
            'passwd':args.mysqldb[2], 'db': args.mysqldb[3]}
    else:
        host = "10.100.100.232"
        user="consulta"
        passwd="consulta"
        db="seiscomp3"
        MySQLdb_dict= {'host':host, 'user':user, 'passwd':passwd, 'db': db}

    if args.radial != None:
        myquery = qy.Query(MySQLdb_dict,args.mode)
        q = myquery.radial_SQLquery(lat=args.radial[0],lon=args.radial[1],ratio=args.radial[2],
                                initial_date=args.start, final_date=args.end,
                                min_mag=args.min_mag, max_mag=args.max_mag, 
                                min_prof=args.min_prof,  max_prof=args.max_prof,
                                event_type=args.event_type,station_list=args.station_list,
                                sort = ['time_event'],to_csv=args.out)
    elif args.id != None:
        myquery = qy.Query(MySQLdb_dict,args.mode)
        q = myquery.id_SQLquery(loc_id=args.id, 
                                initial_date=args.start, final_date=args.end,
                                min_mag=args.min_mag, max_mag=args.max_mag, 
                                min_prof=args.min_prof,  max_prof=args.max_prof,
                                event_type=args.event_type,station_list=args.station_list,
                                sort = ['time_event'],to_csv=args.out)
    else: 
        myquery = qy.Query(MySQLdb_dict,args.mode)
        q = myquery.simple_SQLquery(initial_date=args.start, final_date=args.end,
                                min_mag=args.min_mag, max_mag=args.max_mag, 
                                min_prof=args.min_prof,  max_prof=args.max_prof,
                                event_type=args.event_type,station_list=args.station_list,
                                sort = ['time_event'],to_csv=args.out)