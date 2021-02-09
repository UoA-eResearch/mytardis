import React, { useState, useEffect } from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import PropTypes from "prop-types";
import Datetime from "react-datetime";
import moment from "moment";

import "./DateRangeFilter.css";

// React Datetime requires CSS to work.
import "react-datetime/css/react-datetime.css";

import DatePicker from 'react-date-picker';
const DATE_FORMAT = "YYYY-MM-DD";

const isNone = (value) => {
    // We need empty string to represent an empty field for text fields
    return value === undefined || value === null || value === "";
};

/**
 * Checks if a filter value doesn't have actual value in it.
 * @param {*} value The local value to check.
 */
const isValueEmpty = (value) => {
    if (isNone(value)) {
        return true;
    }
    const { start, end } = value;
    // A number range filter value is empty if both values are null values.
    return isNone(start) && isNone(end);
};

/**
 * Converts the value we are using in this filter to the format expected by the search API.
 * @param {*} localValue The local value to convert
 */
const toSubmitValue = localValue => {
    // console.log(localValue);
    // Replace empty string value with null to represent null parameter value.
    if (!localValue) {
        return null;
    }
    const submitValue = [];
    if (!isNone(localValue.start)) {
        submitValue.push({
            op: ">=",
            content: moment(localValue.start, 'd-M-y').format(DATE_FORMAT)
        });
    }
    if (!isNone(localValue.end)) {
        submitValue.push({
            op: "<=",
            content: moment(localValue.end, 'd-M-y').format(DATE_FORMAT)
        });
    }
    if (submitValue.length === 0) {
        // Return a null to represent no filter value.
        return null;
    }
    return submitValue;
};

/**
 * Converts value in search API format to the value used in this filter.
 * @param {*} submitValue The value in the search API format
 */
const toLocalValue = submitValue => {
    if (!submitValue) {
        return { start: "", end: "" };
    }
    if (!Array.isArray(submitValue)) {
        submitValue = [submitValue];
    }
    const localValue = { start: "", end: "" };
    const startValue = submitValue.filter(value => value.op === ">=");
    const endValue = submitValue.filter(value => value.op === "<=");
    if (startValue.length > 0) {
        localValue.start = moment(startValue[0].content).toDate();
        // console.log('local val start:: ', localValue.start._d);
        // console.log('local val start:: ', localValue.start.toDate());
    }
    if (endValue.length > 0) {
        localValue.end = moment(endValue[0].content).toDate();
        // console.log('local val start:: ', localValue.end);
    }
    // console.log("Local value converted from API -> filter:: ", localValue);
    // console.log(localValue);
    return localValue;
};

/**
 * Merges options for this filter with defaults, if no value is specified
 * for any of the options. 
 * @param {*} options Original parsed options
 */
function mergeOptionsWithDefaults(options) {
    const newOptions = Object.assign({}, options);
    if (!newOptions.hintStart) {
        const weekAgoDate = moment().subtract(1, "week").format(DATE_FORMAT);
        newOptions.hintStart = `YYYY-MM-DD (e.g. ${weekAgoDate})`;
    }
    if (!newOptions.hintEnd) {
        const todayDate = moment().format(DATE_FORMAT);
        newOptions.hintEnd = `YYYY-MM-DD (e.g. ${todayDate})`;
    }
    return newOptions;
}

const isValidDate = date => {
    return date instanceof moment;
};

const DateRangeFilter = ({ id = "missingFilterName", value, options, onValueChange }) => {
    // Make a copy of the options first.
    options = mergeOptionsWithDefaults(options);

    const [localValue, setLocalValue] = useState(toLocalValue(value));

    useEffect(() => {
        // Update the filter when there is a new value,
        // for when the filter value is externally updated
        // e.g. from URL.
        setLocalValue(toLocalValue(value));
    }, [value]);

    const handleStartValueChange = valueFromForm => {
        // Copy the value object, then assign new value into the start field.
        const newValue = Object.assign({}, localValue);
        newValue.start = valueFromForm;

        // TEST: 
        // newValue.start = moment(valueFromForm, "d-M-y");

        if (isValidDate(newValue.start) && !options.hideEnd) {
            if (isValidDate(newValue.end) && newValue.start.isAfter(newValue.end)) {
                // If new start date is before the end date,
                // we auto-fill end date to be same as start date.
                newValue.end = newValue.start;
            }
        }
        setLocalValue(newValue);
    };

    const handleEndValueChange = valueFromForm => {
        // Copy the value object, then assign new value into the start field.
        const newValue = Object.assign({}, localValue);
        newValue.end = valueFromForm;
        // newValue.end = moment(valueFromForm, "d-M-y");
        if (isValidDate(newValue.end) && !options.hideStart) {
            if (isValidDate(newValue.start) && newValue.end.isBefore(newValue.start)) {
                // If new end date is before the start date,
                // we auto-fill start date to be same as end date.
                newValue.start = newValue.end;
            }
        }
        console.log('end date new val://', newValue);
        setLocalValue(newValue);
    };

    // We should disable the filter button if there's nothing in the filter box.
    // But we should be able to clear a field if there's a value on the filter.
    const canChangeValue = !isValueEmpty(localValue) || !isNone(value);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!canChangeValue) {
            return;
        }
        const newValue = toSubmitValue(localValue);
        console.log("about to call on value change w/ this newValue", newValue);
        onValueChange(newValue);
    };

    // Give the input boxes ids so labels can be tied back to the field.
    const startFieldId = "start-" + id,
        endFieldId = "end-" + id;

    return (
        <Form className="date-range-filter" onSubmit={handleSubmit}>
            {options.hideStart ? null :
                <Form.Group className="date-range-filter__field">
                    <Form.Label htmlFor={startFieldId} srOnly={options.hideLabels}>Start</Form.Label>
                    <DatePicker
                            value={localValue.start}
                            // selected={localValue.start}
                            name={startFieldId}
                            onChange={handleStartValueChange}
                            // key={startFieldId + localValue.start}
                            format={"y-M-d"}
                            nativeInputAriaLabel={startFieldId}
                        />
                </Form.Group>
            }
            {options.hideEnd ? null :
                <Form.Group className="date-range-filter__field">
                    <Form.Label htmlFor={endFieldId} srOnly={options.hideLabels}>End</Form.Label>
                    <DatePicker
                            onChange={handleEndValueChange}
                            // selected={localValue.end}
                            name={endFieldId}
                            value={localValue.end}
                            key={startFieldId + localValue.start}
                            format={"y-M-d"}
                            nativeInputAriaLabel={endFieldId}
                        />
                </Form.Group>
            }
            <Button
                type="submit"
                className="date-range-filter__button"
                aria-label="Filter results"
                variant={canChangeValue ? "secondary" : "outline-secondary"}
            >
                Filter
            </Button>
        </Form>
    );
};

DateRangeFilter.propTypes = {
    id: PropTypes.string.isRequired,
    value: PropTypes.array,
    options: PropTypes.shape({
        hideStart: PropTypes.bool,
        hideEnd: PropTypes.bool,
        hintStart: PropTypes.string,
        hintEnd: PropTypes.string,
        hideLabels: PropTypes.bool
    }),
    onValueChange: PropTypes.func.isRequired
};

export default DateRangeFilter;