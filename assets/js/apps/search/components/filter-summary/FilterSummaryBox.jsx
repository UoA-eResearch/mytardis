import React, { Fragment, useCallback } from "react";
import PropTypes from "prop-types";
import { Badge, Button } from "react-bootstrap";
import "./FilterSummaryBox.css";
import { useDispatch, useSelector } from "react-redux";
import { 
    resetFilters, 
    schemaParamFilterValueSelector, 
    schemaParamSelector, 
    schemaSelector, 
    schemaTypeSelector,
    typeAttrSelector, 
    typeSelector,
    typeAttrFilterValueSelector
} from "../filters/filterSlice";
import { 
    runSearch,
    updateSearchTerm,
    searchHasCriteriaSelector
} from "../searchSlice";

function InvalidFilterBadge() {
    return <Badge variant="secondary">(Invalid filter)</Badge>;
}

function AndOperatorBadge() {
    return <Badge variant="info" className="filter-summarybox__badge--separator">AND</Badge>;
}

function MultiValueContentBadge({ content }) {
    return content.map(filterValue =>
        <Badge
            variant="secondary"
            className="filter-summary-box__badge"
        >
            {filterValue}
        </Badge>);
}

function SingleValueContentBadge({ content }) {
    return <Badge 
        variant="secondary"
        className="filter-summary-box__badge"
    >
        {content}
    </Badge>;
}

function FilterBadge({fieldName, value}) {
    return <div className="filter-summary-box__badge-group">
        <Badge variant="secondary" className="filter-summary-box__badge">{fieldName}</Badge>
        {value.map(({op, content}) => 
            <>
                <Badge variant="info" className="filter-summary-box__badge">{op}</Badge>
                {op === "is" ? 
                    <MultiValueContentBadge content={content} />
                    : <SingleValueContentBadge content={content} />}
            </>
        )}
    </div>;

}

FilterBadge.propTypes = {
    typeId: PropTypes.string.isRequired,
    fieldName: PropTypes.string.isRequired,
    value: PropTypes.arrayOf(PropTypes.shape({
        op: PropTypes.string.isRequired,
        content: PropTypes.any.isRequired
    })).isRequired
};

function SchemaParameterFilterBadge({fieldInfo}) {
    const schemaId = fieldInfo.target[0], parameterId = fieldInfo.target[1];
    const typeId = useSelector(state => schemaTypeSelector(state.filters, schemaId));
    const fullFieldName = useSelector(state => {
        const type = typeSelector(state.filters, typeId);
        const schema = schemaSelector(state.filters, schemaId); 
        const schemaParam = schemaParamSelector(state.filters, schemaId, parameterId);
        if (!type || !schema || !schemaParam) {
            return "";
        } else {
            return `${type.full_name}.${schema.schema_name}.${schemaParam.full_name}`; 
        }
    });
    if (fullFieldName === "") {
        return <InvalidFilterBadge />;
    } else {
        const filterValue = useSelector(
            state => schemaParamFilterValueSelector(state.filters, schemaId, parameterId)
        );
        return <FilterBadge typeId={typeId} fieldName={fullFieldName} value={filterValue} />;
    }
}

function TypeAttributeFilterBadge({fieldInfo}) {
    const typeId = fieldInfo.target[0], attributeId = fieldInfo.target[1];
    const fullFieldName = useSelector(state => {
        // Remove the extra s
        const type = typeSelector(state.filters, typeId.substring(0, typeId.length - 1));
        const attribute = typeAttrSelector(state.filters, typeId, attributeId);
        if (!type || !attribute) {
            return "";
        } else {
            return `${type.full_name}.${attribute.full_name}`;
        }
    });
    if (fullFieldName === "") {
        return <InvalidFilterBadge />;
    } else {
        const filterValue = useSelector(
            state => typeAttrFilterValueSelector(state.filters, typeId, attributeId)
        );
        return <FilterBadge typeId={typeId} fieldName={fullFieldName} value={filterValue} />;
    }
}

function QuickSearchBadge({typeId, searchTerm}) {
    const type = useSelector(
        state => typeSelector(state.filters, typeId)
    );
    if (!type || !searchTerm) {
        return <InvalidFilterBadge />;
    } else {
        const searchTermAsBadgeValue = [{
            op: "contains",
            content: searchTerm
        }];
        return <FilterBadge
            fieldName={type.full_name} 
            typeId={typeId} 
            value={searchTermAsBadgeValue} 
        />;
    }
}

function QuickSearchBadgeList() {
    const searchTermsById = useSelector(
        state => state.search.searchTerm || {}
    );
    const typesWithSearchTerms = Object.keys(searchTermsById);
    return <>{
        typesWithSearchTerms.map((typeId, index) => {
            const isLastFilter = index === typesWithSearchTerms.length - 1;
            return <Fragment key={typeId + "-search-term"}>
                <QuickSearchBadge
                    typeId={typeId}
                    searchTerm={searchTermsById[typeId]}
                />
                {!isLastFilter ? <AndOperatorBadge /> : null}
            </Fragment>;
        })
    }</>;
}

function getFilterBadge(filterKind) {
    switch (filterKind) {
        case "typeAttribute":
            return TypeAttributeFilterBadge;
        case "schemaParameter":
            return SchemaParameterFilterBadge;
        default:
            break;
    } 
};

function FilterSummaryFilterList() {
    const activeFiltersByTypeId = useSelector(state => state.filters.activeFilters);
    const activeFilters = [];
    for (const typeId in activeFiltersByTypeId) {
        activeFiltersByTypeId[typeId].forEach(filter => {
            activeFilters.push(filter);
        });
    }

    return <>
        {activeFilters.map((filter, index) => {
            const isLastFilter = index === activeFilters.length - 1;
            const ApplicableFilterBadge = getFilterBadge(filter.kind);
            return <Fragment key={filter.kind + filter.target.join(",")}>
                <ApplicableFilterBadge fieldInfo={filter} />
                {!isLastFilter ? <AndOperatorBadge /> : null}
            </Fragment>;
        })
        }
    </>;
}

function ResetFiltersButton() {
    const dispatch = useDispatch();
    const onResetFilters = useCallback(
        () => {
            dispatch(resetFilters());
            dispatch(updateSearchTerm({
                searchTerm: {},
                replaceState: true
            }));
            dispatch(runSearch());
        },
        [dispatch]
    );
    const hasActiveFiltersOrSearchTerm = useSelector(state => 
        searchHasCriteriaSelector(state.search, state.filters)
    );
    return <Button 
        className="ms-1"
        onClick={onResetFilters} 
        variant={hasActiveFiltersOrSearchTerm ? "primary" : "outline-secondary"}
    >
        Reset filters
    </Button>;
}

function BadgeList() {
    const searchHasCriteria = useSelector(
        state => searchHasCriteriaSelector(state.search, state.filters)
    );
    if (searchHasCriteria) {
        return <>
        <QuickSearchBadgeList />
        <AndOperatorBadge />
        <FilterSummaryFilterList />
    </>;
    } else {
        return <p>Use options on the left to narrow down your results.</p>;
    }
}
export default function FilterSummaryBox() {
    return (
        <div className="card" style={{padding: "1rem"}}>
            <div className="card-body d-flex">
                <div className="flex-grow-1 h5">
                    <BadgeList />
                </div>
                <div>
                    <ResetFiltersButton />
                </div>
            </div>
        </div>
    );
}