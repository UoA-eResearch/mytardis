import TextFilter from "./text-filter/TextFilter";
import NumberRangeFilter from "./range-filter/NumberRangeFilter";
import DateRangeFilter from "./date-filter/DateRangeFilter";
import CategoryFilter from "./category-filter/CategoryFilter";

/**
 * @param {*} type Simple mapper function that returns 
 * the appropriate filter component based on filter type. 
 */
export const mapTypeToFilter = (type) => {
    switch (type) {
        case "STRING":
            return TextFilter;
        case "NUMERIC":
            return NumberRangeFilter;
        case "DATETIME":
            return DateRangeFilter;
        case "CATEGORICAL":
            return CategoryFilter;
        default:
            return TextFilter;
    }
}