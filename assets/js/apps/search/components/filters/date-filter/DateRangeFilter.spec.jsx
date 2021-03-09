/*eslint-env jest*/

import { Default, Empty } from "./DateRangeFilter.stories";
import { render, fireEvent, waitFor, screen } from "@testing-library/react";
import React from "react";

const getDateFields = (screenInstance) => (
    [
        screen.getByLabelText("Start Date"),
        screen.getByLabelText("End Date"),
        screen.getByText("Filter"),
        screen.getByLabelText("Start Day"),
        screen.getByLabelText("Start Month"),
        screen.getByLabelText("Start Year"),
        screen.getByLabelText("End Day"),
        screen.getByLabelText("End Month"),
        screen.getByLabelText("End Year"),
    ]
);

it("should render start and end dates as specified", async () => {
    render(<Default {...Default.args} onValueChange={() => {}} />);
    const [startDateEl, endDateEl] = getDateFields(screen);
    expect(startDateEl.value).toBe("2020-01-05");
    expect(endDateEl.value).toBe("2020-05-28");
});

it("should change start date when end date becomes a date before it", async () => {
    render(<Default {...Default.args} onValueChange={() => {}} />);
    let [startDateEl, endDateEl] = getDateFields(screen);
    const anotherDate = "2019-12-30";
    fireEvent.change(endDateEl, { target: {value: anotherDate } });
    // After changing the end date to an earlier date, 
    // we should see both the start and end date fields to be the same
    // Retrieve input elements again as we have replaced them
    // to get around the react-datetime bug.
    // https://github.com/arqex/react-datetime/issues/760

    [startDateEl, endDateEl] = getDateFields(screen);
    await waitFor(() => expect(endDateEl.value).toBe(anotherDate));
    await waitFor(() => expect(startDateEl.value).toBe(anotherDate));
});

it("should callback with right value after submitting", async () => {
    const mockHandleChangeFn = jest.fn();
    // Add mock handleChange function to monitor whether changes
    // are added.
    const props = Object.assign({}, Empty.args, {
        onValueChange: mockHandleChangeFn
    });
    render(<Empty {...props} />);
    const [startDateEl, endDateEl,filterButton ] = getDateFields(screen);


    // Calling change screen.getByLabel seems to work whereas the using consts doesnt
    // updating start field values
    fireEvent.change(screen.getByLabelText("Start Day"), {target: {value: "01"}});
    fireEvent.change(screen.getByLabelText("Start Month"), {target: {value: "02"}});
    fireEvent.change(screen.getByLabelText("Start Year"), {target: {value: "2023"}});

    // updating end field values
    fireEvent.change(screen.getByLabelText("End Day"), {target: {value: "04"}});
    fireEvent.change(screen.getByLabelText("End Month"), {target: {value: "05"}});
    fireEvent.change(screen.getByLabelText("End Year"), {target: {value: "2026"}});

    fireEvent.click(filterButton);
    await waitFor(
        () => {
            expect(mockHandleChangeFn).toHaveBeenCalledTimes(1);
            expect(mockHandleChangeFn).toBeCalledWith(
                [
                    {op:">=",content:"2023-02-01"},
                    {op:"<=",content: "2026-05-04"}
                ]
            );
        }
    );
});

it("should callback with null after clearing a filter", async () => {
    const mockHandleChangeFn = jest.fn();
    const props = Object.assign({}, Default.args, {
        onValueChange: mockHandleChangeFn
    });
    render(<Default {...props} />);
    const [startDateEl, endDateEl,filterButton ] = getDateFields(screen);

    // Clear the dates
    fireEvent.click(screen.getByLabelText("Clear Start"));
    fireEvent.click(screen.getByLabelText("Clear End"));

    // Filter button should still be clickable to clear the field.
    expect(filterButton.disabled).toBeFalsy();
    fireEvent.click(filterButton);
    await waitFor(
        () => {
            expect(mockHandleChangeFn).toHaveBeenCalledTimes(1);
            expect(mockHandleChangeFn).toBeCalledWith(null);
        });
});