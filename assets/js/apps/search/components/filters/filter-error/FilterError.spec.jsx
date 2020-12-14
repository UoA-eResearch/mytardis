import { Default, CustomMessages, WithLabel } from "./FilterError.stories";
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import addons, { mockChannel } from '@storybook/addons';
import { scryRenderedComponentsWithType } from "react-dom/test-utils";

describe("Filter Error component", () => {
    it('Should show the default error message', () => {
        render(Default());
        const errorText = screen.getByTestId("filter-error-text");
        expect(errorText.innerHTML).toBe("Invalid input");
    })


    // untested
    it('Should show the long error message', () => {
        render(Default());
        const errorText = screen.getByTestId("filter-error-text");
        expect(errorText.innerHTML).toBe("Invalid input");
    })

    // untested
    it('Should contain a long error message', () => {
        render(Default());
        const errorText = screen.getByTestId('long-tooltip');
        expect(errorText.toBe('longer message'));
    })

    // untested
    it('Should contain a custom short error message', () => {
        render(CustomMessages());
        const errorText = screen.getByTestId('long-tooltip');
        expect(errorText.toBe('custom long message'));
    })

    // untested
    it('Should contain a custom short error message', () => {
        render(CustomMessages());
        const errorText = screen.getByTestId('filter-errror-text');
        expect(errorText.toBe('custom short message'));
    })  

})
