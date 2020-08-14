import React, { useMemo } from 'react';
import PropTypes from "prop-types";
import Accordion from 'react-bootstrap/Accordion';
import Card from 'react-bootstrap/Card';
import { updateSchemaParameter, typeAttrSelector } from "../filterSlice";
import { useDispatch, useSelector } from "react-redux";
import CategoryFilter from '../category-filter/CategoryFilter';
import { runSearch } from '../../searchSlice';
import { mapTypeToFilter } from "../index";

// A hook for converting a hashmap of values into a list.
const useAsList = (jsObject = {}) => (
    useMemo(() => (
        Object.keys(jsObject)
                .map(key => jsObject[key]))
    ,[jsObject])
);

const SchemaFilterList = ({ schema }) => {
    const { id: schemaId, type: schemaType, parameters } = schema,
            paramsAsList = useAsList(parameters),
            dispatch = useDispatch();

    return (<>
        {paramsAsList.map(
                param => {
                    const { value, data_type: parameterType, full_name, id: parameterId } = param,
                            setParamValue = (value) => {
                                dispatch(updateSchemaParameter({
                                    schemaId,
                                    parameterId,
                                    value
                                }));
                                dispatch(runSearch());
                            },
                            ApplicableFilter = mapTypeToFilter(param.data_type);
                    return (
                            <section key={parameterId} className="single-schema-list__filter">
                                <h5 className="single-schema-list__filter-label">{full_name}</h5>
                                <ApplicableFilter 
                                    id={schemaId+"."+parameterId}
                                    value={value}
                                    onValueChange={setParamValue} />
                                <hr />
                            </section>
                    );
                }
        )}
    </>);
    
}

SchemaFilterList.propTypes = {
    schema: PropTypes.object.isRequired 
}

const TypeSchemaList = ({ typeId }) => {
    const schemasAsList = useSelector(state => {return state.filters.typeSchemas[typeId]});
    const { byId: schemas } = useSelector(state => (state.filters.schemas)) || { byId: {}};
    const schemaValue = useSelector((state) => (
        typeAttrSelector(state.filters, typeId, "schema").value
    ));
    const onValueChange =
        (value) => {
            batch(() => {
                dispatch(updateActiveSchemas({ typeId, value }));
                dispatch(runSearch());
            });
        };

    let activeSchemas;
    if (!schemaValue) {
        // If there is no filter on what schemas to show, we show all of them.
        activeSchemas = schemasAsList;
    } else {
        activeSchemas = schemaValue.content;
    }

    const schemaList = useMemo(() => (
        // Return the schema list in format expected by CategoryFilter
        {
            allIds: schemasAsList,
            byId: schemasAsList.reduce((acc,schemaId) => {
                acc[schemaId] = {
                    label: schemas[schemaId].schema_name
                };
                return acc;
            },{})
        }
    ),[schemasAsList, schemas]);

    if (schemasAsList.length === 0) {
        return null;
    }

    return (
        <section>
            <h3 className="h5">Schemas</h3>
            <CategoryFilter value={schemaValue} onValueChange={onValueChange} options={{
                checkAllByDefault: true,
                categories: schemaList
            }} />
            <Accordion>
                {schemasAsList.map((id) => {
                    const schema = schemas[id],
                        name = schema.schema_name;
                    if (!activeSchemas.includes(id)) {
                        // If schema is not selected, don't show filters for the schema.
                        return null;
                    }
                    return (
                        <Card key={name}>
                            <Card.Header>
                                <Accordion.Toggle as="button" className="btn btn-link" eventKey={id}>
                                    {name} filters
                                </Accordion.Toggle>
                            </Card.Header>
                            <Accordion.Collapse eventKey={id}>
                                <Card.Body>
                                    <SchemaFilterList schema={schema} />
                                </Card.Body>
                            </Accordion.Collapse>
                        </Card>
                    );
                })}
            </Accordion>
        </section>
    );
};

TypeSchemaList.propTypes = {
    typeId: PropTypes.string.isRequired
};

export default TypeSchemaList;