$(document).ready(function() {
    function updateEquivalentNPR(row) {
        var rate = parseFloat(row.find("td:eq(3)").text());
        var unit = parseFloat(row.find("td:eq(2)").text());
        var deno = parseFloat(row.find("td:eq(1)").text());

        if (!isNaN(rate) && !isNaN(unit) && !isNaN(deno)) {
            var equivalentNPR = rate * unit * deno;
            row.find("td:eq(4)").text(equivalentNPR.toFixed(2));
            return equivalentNPR;
        } else {
            return NaN;
        }
    }

    function updateTotalEquivalentNPR() {
        var totalEquivalentNPR = 0;
        $("tbody tr").each(function() {
            var equivalentNPR = updateEquivalentNPR($(this));
            if (!isNaN(equivalentNPR)) {
                totalEquivalentNPR += equivalentNPR;
            }
        });

        $("#totalEquivalentNPR").val(totalEquivalentNPR.toFixed(2));
    }

    $("tbody").on("click", ".editButton", function(event) {
        event.preventDefault();

        var row = $(this).closest("tr");
        var columnsToEdit = [3, 2, 1]; // Indexes of columns rate, unit, and deno
        
        row.find("td:not(:last-child)").each(function(index) {
            if (columnsToEdit.indexOf(index) !== -1) {
                var cellText = $(this).text();
                $(this).html("<input class='form-controls' type='text' name='" + getFieldName(index) + "' value='" + cellText + "'>");
            }
        });

        function getFieldName(index) {
            switch (index) {
                case 1:
                    return 'deno';
                case 2:
                    return 'unit';
                case 3:
                    return 'rate';
                default:
                    return '';
            }
        }

        row.find(".editButton").addClass("saveButton").removeClass("editButton").html('<i class="fas fa-save"></i>');
    });

    $("tbody").on("click", ".saveButton", function(event) {
        event.preventDefault();

        var row = $(this).closest("tr");
        row.find("input").each(function() {
            var cellText = $(this).val();
            $(this).parent("td").text(cellText);
        });

        row.find(".saveButton").addClass("editButton").removeClass("saveButton").html('<i class="fas fa-edit"></i>');

        updateEquivalentNPR(row);
        updateTotalEquivalentNPR();

        
        var totalEquivalentNPRValue = $('#totalEquivalentNPR').val();
        var row = $(this).closest("tr");
        var fcyId = row.attr('id');
        var denoValue = $("#deno-" + fcyId).text();  
        var unitValue = $("#unit-" + fcyId).text();  
        var rateValue = $("#rate-" + fcyId).text();
        if (denoValue === '' || denoValue === '0' ||
            unitValue === '' || unitValue === '0' ||
            rateValue === '' || rateValue === '0') {
            alert('Error: Fields cannot be empty or zero.');
        }else{
            var equivalentNPRValue = $("#equivalentNPR-" + fcyId).text();  
            var masterId = "{{ fcyrequest.id }}";
    
            if (totalEquivalentNPRValue.trim() !== '') {
                var csrftoken = getCookie('csrftoken');
    
                $.ajax({
                    method: 'POST',
                    url: '/convert_to_words/', 
                    data: {
                        'totalEquivalentNPR': totalEquivalentNPRValue
                    },
                    dataType: 'json',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    success: function(data) {
                        var totalEquivalentNPRToWords = data.totalEquivalentNPRToWords || 'N/A';
                        $('#totalEquivalentNPRToWords').val(totalEquivalentNPRToWords);
                        var updatedData = {
                            'deno': denoValue,
                            'unit': unitValue,
                            'rate': rateValue,
                            'equivalentNPR':equivalentNPRValue,
                            'totalEquivalentNPRToWords': totalEquivalentNPRToWords,
                            'totalEquivalentNPR': totalEquivalentNPRValue
            
                        };
                        var csrftoken = getCookie('csrftoken'); 
                        $.ajax({
                            method: 'POST',
                            url: '/update_fcy_data/' + fcyId + '/' + masterId + '/', 
                            data: updatedData,
                            dataType: 'json',
                            headers: {
                                'X-CSRFToken': csrftoken
                            },
                            success: function(response) {
                                toastr.success('Data updated successfully');
                            },
                            error: function(error) {
                                toastr.error('Error updating data');
                            },
                            complete: function(xhr, status) {
                                if (status !== 'error') {
                                    window.location.reload(); 
                                }
                            }
                            
                        });
                    }
                });
            } else {
                $('#totalEquivalentNPRToWords').val('');
            }
        }  

    });

    $("tbody").on("input", "td:lt(4)", function() {
        var row = $(this).closest("tr");
        updateEquivalentNPR(row);
        updateTotalEquivalentNPR();
    });
    
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
    