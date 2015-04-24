# print_table is a basic function which will take a list of lists
# and print them as a formatted table with all columns aligned to
# their first character
# A. Whitbeck, March 16, 2014

def get_column_width( column = [] ) :
    
    column_len = []
    for i in column :
        column_len.append( len( i ) )

    return max( column_len )

def get_column_widths( table = [] ) : 

    column_width = []
    columns = zip(*table)  # unzips (transposes) table    

    for column in columns : 
        column_width.append( get_column_width( column ) )

    return column_width

def print_table( table = [] ) : 
    
    column_width = get_column_widths( table )    

    for word in table : 
        print '  '.join( [ str( word[ i ] ) + ' ' * ( column_width[ i ] - len( word[ i ] ) ) for i in range( len( word ) ) ] ) 


