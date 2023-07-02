is_a(samsung_c430w, printer).

has_function(printer, printing).
has_function(printer, black_white_printing).
has_function(printer, single_sided_printing).
has_function(printer, scanning).
has_function(printer, wireless_printing).

can_do(Device, Job) :- is_a(Device, X), has_function(X, Job).



has_solution(jammed_paper, clear_paper_jam).

has_solution(sticked_paper, use_correct_type_of_paper).
has_solution(sticked_paper, check_paper_capacity).
has_solution(sticked_paper, fan_paper).

has_solution(no_power, check_power_cord_connections).
has_solution(no_power, check_power_switch_and_source).

has_solution(no_cable_connection, disconnect_and_reconnect_cable).

has_solution(no_wireless_connection, check_port_setting).

has_solution(no_driver, uninstall_and_reinstall_driver).

has_solution(full_output_tray, remove_paper_from_output_tray).

has_solution(complex_jobs, reduce_page_complexity).
has_solution(complex_jobs, adjust_print_quality_settings).

has_solution(incorrect_orientation, change_page_orientation).

has_solution(no_matching_paper_sizes, use_correct_pager_size).

has_solution(out_of_toner, redistribute_toner).

has_solution(blank_documents, check_files_containing_blank_pages).

has_solution(low_toner_supply, replace_toner_cartridge).

has_solution(dirty_roller_and_paper_path, clean_inside_machine).

has_solution(scratched_imaging_unit, replace_imaging_unit).

caused_by(no_paper_feed, jammed_paper).
caused_by(no_paper_feed, sticked_paper).

caused_by(no_printing, no_power).
caused_by(no_printing, no_cable_connection).
caused_by(no_printing, no_wireless_connection).
caused_by(no_printing, no_driver).
caused_by(no_printing, full_output_tray).

caused_by(slow_printing, complex_jobs).

caused_by(half_blank_pages, incorrect_orientation).
caused_by(half_blank_pages, no_matching_paper_sizes).

caused_by(blank_pages, out_of_toner).
caused_by(blank_pages, blank_documents).

caused_by(low_quality_print, low_toner_supply).
caused_by(low_quality_print, dirty_roller_and_paper_path).
caused_by(low_quality_print, scratched_imaging_unit).

fix(Issue, Solution) :- caused_by(Issue, X), has_solution(X, Solution).
