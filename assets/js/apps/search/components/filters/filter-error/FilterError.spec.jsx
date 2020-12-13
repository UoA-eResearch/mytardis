import { Default } from "./FilterError.stories";
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import addons, { mockChannel } from '@storybook/addons';
import { scryRenderedComponentsWithType } from "react-dom/test-utils";

describe("Filter Error component", () => {
    it('Should show the default error message', () => {
        render(Default());
        const errorText = screen.getByTestId("filter-error-text");
        expect(errorText.innerHTML).toBe("Invalid input");
    })


    it('Should show the long error message', () => {
        render(Default());
        const errorText = screen.getByTestId("filter-error-text");
        expect(errorText.innerHTML).toBe("Invalid input");
    })
})
