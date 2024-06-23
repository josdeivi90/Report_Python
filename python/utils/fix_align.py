def fix_align(align_list, new_len):
    
    len_align_list = len(align_list)
    new_align_list = align_list[:]
    
    while len(new_align_list) > new_len:
        new_align_list.pop(0)
    len_new_align_list = len(new_align_list)
    
    if len_new_align_list < len_align_list:
        new_align_list[0] = 'left'
        new_align_list[1] = 'left'
        new_align_list[-1] = 'center'

    return new_align_list
