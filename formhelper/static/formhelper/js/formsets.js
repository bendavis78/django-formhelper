/**
 * Django admin inlines
 *
 * Based on jQuery Formset 1.1
 * @author Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
 * @requires jQuery 1.2.6 or later
 *
 * Copyright (c) 2009, Stanislaus Madueke
 * All rights reserved.
 *
 * Spiced up with Code from Zain Memon's GSoC project 2009
 * modified for Django by Jannis Leidel
 * modified for django-formhelper by Ben Davis
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function($) {
    $.fn.formset = function(opts) {
        var options = $.extend({}, $.fn.formset.defaults, opts);
        var updateElementIndex = function(el, prefix, ndx) {
            var id_regex = new RegExp("(" + prefix + "-\\d+)");
            var replacement = prefix + "-" + ndx;
            if ($(el).attr("for")) {
                $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
            }
            if (el.id) {
                el.id = el.id.replace(id_regex, replacement);
            }
            if (el.name) {
                el.name = el.name.replace(id_regex, replacement);
            }
        };
        var template = $("." + options.prefix + "-form.empty-form");
        if (!template.length) {
          throw new Error("Cannod find empty-form: ."+options.prefix+".empty-form");
        }
        template.hide();
        var totalForms = $("#id_" + options.prefix + "-TOTAL_FORMS").attr("autocomplete", "off");
        var maxForms = $("#id_" + options.prefix + "-MAX_NUM_FORMS").attr("autocomplete", "off");
        // only show the add button if we are allowed to add more items,
        // note that max_num = None translates to a blank string.
        var showAddButton = maxForms.val() == '' || (maxForms.val()-totalForms.val()) > 0;
        var $this = $(this);
        $this.each(function(i) {
            $this.not("." + options.emptyCssClass).addClass(options.formCssClass);
        });
        if ($this.length && showAddButton) {
            var addButton;
            if ($this.attr("tagName") == "TR") {
                // If forms are laid out as table rows, insert the
                // "add" button in a new table row:
                var numCols = this.eq(0).children().length;
                $this.parent().append('<tr class="' + options.addCssClass + '"><td colspan="' + numCols + '"><a id="formset_add_btn" href="javascript:void(0)" title="' + options.addTitle + '">' + options.addText + "</a></tr>");
                addButton = $this.parent().find("tr:last a");
            } else {
                // Otherwise, insert it immediately after the last form:
                $this.filter(":last").after('<div class="' + options.addCssClass + '"><a id="formset_add_btn" href="javascript:void(0)" title="' + options.addTitle + '">' + options.addText + "</a></div>");
                addButton = $this.filter(":last").next().find("a");
            }
            var updateAddAnotherText = function(row) {
                var totalForms = $("#id_" + options.prefix + "-TOTAL_FORMS").val();
                var addText = options.addText;
                var addTitle = options.addTitle;
                if (totalForms == "0") {
                    addText = options.addTextInitial ? options.addTextInitial : options.addText;
                    addTitle = options.addTitleInitial ? options.addTitleInitial : options.addTitle;
                } else {
                    addText = options.addText;
                    addTitle = options.addTitle;
                }
                $('#formset_add_btn').text(addText);
                $('#formset_add_btn').attr('title', addTitle);
            }
            // Makes sure all delete links are assigned a click handler
            var updateDeleteLinks = function(row) {
                // The delete button of each row triggers a bunch of other things
                var deleteCssSelector = options.deleteCssClass.replace(/ /g, '.');
                row.find("a." + deleteCssSelector).click(function() {
                    // Remove the parent form containing this button:
                    var row = $(this).parents("." + options.formCssClass);

                    // triger formset removal
                    row.trigger('formsetremove');

                    // Update the TOTAL_FORMS form count.
                    var forms = $("." + options.formCssClass);
                    $("#id_" + options.prefix + "-TOTAL_FORMS").val(forms.length-1);
                    // Show add button again once we drop below max
                    if ((maxForms.val() == '') || (maxForms.val()-forms.length) > 0) {
                        addButton.parent().show();
                    }
                    // Also, update names and ids for all remaining form controls
                    // so they remain in sequence:
                    for (var i=0, formCount=forms.length; i<formCount; i++)
                    {
                        $(forms.get(i)).find("input,select,textarea,label,a").each(function() {
                            updateElementIndex(this, options.prefix, i);
                        });
                    }
                    updateAddAnotherText(row);
                    return false;
                });
            }
            addButton.click(function() {
                var totalForms = $("#id_" + options.prefix + "-TOTAL_FORMS");
                var nextIndex = parseInt(totalForms.val());
                var template = $("." + options.prefix + "-form.empty-form");
                var row = template.clone(true);
                row.removeClass(options.emptyCssClass)
                    .addClass(options.formCssClass)
                    .attr("id", options.prefix + "-" + nextIndex)
                    .insertBefore($(template));
                row.show()
                row.find("*")
                    .filter(function() {
                        var el = $(this);
                        return el.attr("id") && el.attr("id").search(/__prefix__/) >= 0;
                    }).each(function() {
                        var el = $(this);
                        el.attr("id", el.attr("id").replace(/__prefix__/g, nextIndex));
                    })
                    .end()
                    .filter(function() {
                        var el = $(this);
                        return el.attr("name") && el.attr("name").search(/__prefix__/) >= 0;
                    }).each(function() {
                        var el = $(this);
                        el.attr("name", el.attr("name").replace(/__prefix__/g, nextIndex));
                    })
                    .end()
                    .filter(function() {
                        var el = $(this);
                        return el.attr("for") && el.attr("for").search(/__prefix__/) >= 0;
                    }).each(function() {
                        var el = $(this);
                        el.attr("for", el.attr("for").replace(/__prefix__/g, nextIndex));
                    });
                if (row.is("tr")) {
                    // If the forms are laid out in table rows, insert
                    // the remove button into the last table cell:
                    row.children(":last").append('<div><a class="' + options.deleteCssClass +'" href="javascript:void(0)">' + options.deleteText + "</a></div>");
                } else if (row.is("ul") || row.is("ol")) {
                    // If they're laid out as an ordered/unordered list,
                    // insert an <li> after the last list item:
                    row.append('<li><a class="' + options.deleteCssClass +'" href="javascript:void(0)">' + options.deleteText + "</a></li>");
                } else {
                    // Otherwise, just insert the remove button as the
                    // last child element of the form's container:
                    row.children(":last").append('<span><a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText + "</a></span>");
                }

                // hide the delete box for dynamically-added forms
                row.find('.field.DELETE').hide();

                row.find("input,select,textarea,label,a").each(function() {
                    updateElementIndex(this, options.prefix, totalForms.val());
                });
                // Update number of total forms
                $(totalForms).val(nextIndex + 1);
                // Hide add button in case we've hit the max, except we want to add infinitely
                if ((maxForms.val() != '') && (maxForms.val()-totalForms.val()) <= 0) {
                    addButton.parent().hide();
                }
                updateDeleteLinks(row);
                updateAddAnotherText(row);

                // setup removal trigger
                row.on('formsetremove', function(){
                  $(this).remove();
                });

                // trigger formset added event
                row.trigger('formsetadd');

                return false;
            });
            updateDeleteLinks($this);
            updateAddAnotherText($this);
            $this.filter("." + options.emptyCssClass).hide()
            
        }
        return this;
    }
    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: "form",                 // The form prefix for your django formset
        addText: "add another",         // Text for the add link
        addTitle: "click here to add another", // Tooltip for the add link
        deleteText: "remove",           // Text for the delete link
        addCssClass: "add-link",         // CSS class applied to the add link
        deleteCssClass: "delete-link",   // CSS class applied to the delete link
        emptyCssClass: "empty-form",     // CSS class applied to the empty row
        formCssClass: "dynamic-form",   // CSS class applied to each form in a formset
        added: null,                    // Function called each time a new form is added
        removed: null                   // Function called each time a form is deleted
    }
})(jQuery);
