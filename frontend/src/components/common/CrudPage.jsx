import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  useSearchParams,
} from "react-router-dom";

import {
  Edit3,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  X,
} from "lucide-react";

import api from "../../api/client";
import "../../styles/crud.css";


const EMPTY_FIELDS = Object.freeze([]);
const EMPTY_ROW_ACTIONS = Object.freeze([]);


function createEmptyForm(
  fields
) {
  const result = {};

  fields.forEach(
    (field) => {

      if (
        field.type ===
        "checkbox"
      ) {
        result[field.name] =
          field.defaultValue ??
          false;

      } else {
        result[field.name] =
          field.defaultValue ??
          "";
      }

    }
  );

  return result;
}


function preparePayload(
  form,
  fields,
  editing
) {
  const payload = {
    ...form,
  };

  fields.forEach(
    (field) => {

      if (
        field.readOnly
      ) {
        delete payload[
          field.name
        ];

        return;
      }

      if (
        field.createOnly &&
        editing
      ) {
        delete payload[
          field.name
        ];

        return;
      }

      if (
        field.nullable &&
        (
          payload[
            field.name
          ] === "" ||
          payload[
            field.name
          ] === undefined
        )
      ) {
        payload[
          field.name
        ] = null;
      }

      if (
        field.type ===
          "number" &&
        payload[
          field.name
        ] !== "" &&
        payload[
          field.name
        ] !== null
      ) {
        payload[
          field.name
        ] = Number(
          payload[
            field.name
          ]
        );
      }

    }
  );

  return payload;
}


export default function CrudPage({
  title,
  description,
  endpoint,
  columns,
  fields = EMPTY_FIELDS,
  allowCreate = true,
  allowEdit = true,
  allowDelete = true,
  rowActions = EMPTY_ROW_ACTIONS,
}) {

  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams();

  const [rows, setRows] =
    useState([]);

  const [meta, setMeta] =
    useState({
      count: 0,
      next: null,
      previous: null,
    });

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  const [search, setSearch] =
    useState("");

  const [page, setPage] =
    useState(1);

  const [showForm, setShowForm] =
    useState(false);

  const [editing, setEditing] =
    useState(null);

  const [form, setForm] =
    useState(() =>
      createEmptyForm(
        fields
      )
    );

  const [options, setOptions] =
    useState({});

  const urlConsumedRef =
    useRef(false);

  const controllerRef =
    useRef(null);


  /* =====================================================
     SOURCE FIELDS
  ===================================================== */

  const sourceFields =
    useMemo(() => {

      return fields.filter(
        (field) =>
          field.source
      );

    }, [fields]);


  /* =====================================================
     LOAD OPTIONS
  ===================================================== */

  const loadOptions =
    useCallback(
      async () => {

        if (
          sourceFields.length === 0
        ) {
          return;
        }

        const result = {};

        await Promise.all(
          sourceFields.map(
            async (
              field
            ) => {

              try {

                const response =
                  await api.get(
                    field.source,
                    {
                      params: {
                        page_size:
                          500,
                      },
                    }
                  );

                result[
                  field.name
                ] =
                  response.data
                    ?.results ??
                  response.data ??
                  [];

              } catch (
                error
              ) {

                console.error(
                  `Unable to load ${field.name}`,
                  error
                );

                result[
                  field.name
                ] = [];

              }

            }
          )
        );

        setOptions(
          (
            current
          ) => {

            if (
              current === result
            ) {
              return current;
            }

            return result;
          }
        );

      },
      [sourceFields]
    );


  /* =====================================================
     LOAD ROWS
  ===================================================== */

  const loadRows =
    useCallback(
      async () => {

        if (
          controllerRef.current
        ) {
          controllerRef.current.abort();
        }

        const controller =
          new AbortController();

        controllerRef.current =
          controller;

        setLoading(
          true
        );

        setError("");

        try {

          const params = {
            page,
          };

          if (
            search.trim()
          ) {
            params.search =
              search.trim();
          }

          const response =
            await api.get(
              endpoint,
              {
                params,
                signal:
                  controller.signal,
              }
            );

          const data =
            response.data;

          if (
            Array.isArray(
              data
            )
          ) {

            setRows(
              data
            );

            setMeta({
              count:
                data.length,

              next:
                null,

              previous:
                null,
            });

          } else {

            setRows(
              data?.results ??
                []
            );

            setMeta({
              count:
                data?.count ??
                0,

              next:
                data?.next ??
                null,

              previous:
                data?.previous ??
                null,
            });

          }

        } catch (
          error
        ) {

          if (
            error?.code ===
              "ERR_CANCELED" ||
            controller.signal.aborted
          ) {
            return;
          }

          console.error(
            error
          );

          setError(
            error.response
              ?.data?.detail ||
              "Unable to load records."
          );

        } finally {

          if (
            controllerRef.current ===
            controller
          ) {
            controllerRef.current =
              null;

            setLoading(
              false
            );
          }

        }

      },
      [
        endpoint,
        page,
        search,
      ]
    );


  useEffect(() => {

    loadRows();

    return () => {
      if (
        controllerRef.current
      ) {
        controllerRef.current.abort();
      }

      controllerRef.current =
        null;
    };

  }, [loadRows]);


  useEffect(() => {
    loadOptions();
  }, [loadOptions]);


  /* =====================================================
     URL ACTIONS
  ===================================================== */

  useEffect(() => {

    if (
      urlConsumedRef.current
    ) {
      return;
    }

    const create =
      searchParams.get(
        "create"
      );

    const urlSearch =
      searchParams.get(
        "search"
      );


    if (
      urlSearch
    ) {

      setSearch(
        urlSearch
      );

      setPage(1);

    }


    if (
      create === "1" &&
      allowCreate &&
      fields.length > 0
    ) {

      setEditing(
        null
      );

      setForm(
        createEmptyForm(
          fields
        )
      );

      setError("");

      setShowForm(
        true
      );

    }


    if (
      create ||
      urlSearch
    ) {

      const next =
        new URLSearchParams(
          searchParams
        );

      next.delete(
        "create"
      );

      next.delete(
        "search"
      );

      setSearchParams(
        next,
        {
          replace: true,
        }
      );

    }

    urlConsumedRef.current = true;

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    searchParams,
    setSearchParams,
    allowCreate,
    fields,
  ]);


  /* =====================================================
     CREATE
  ===================================================== */

  const openCreate = () => {

    setEditing(
      null
    );

    setForm(
      createEmptyForm(
        fields
      )
    );

    setError("");

    setShowForm(
      true
    );

  };


  /* =====================================================
     EDIT
  ===================================================== */

  const openEdit = (
    row
  ) => {

    setEditing(
      row
    );

    setError("");

    const next =
      createEmptyForm(
        fields
      );

    fields.forEach(
      (field) => {

        let value =
          row[
            field.name
          ];

        if (
          value ===
            null ||
          value ===
            undefined
        ) {
          value = "";
        }

        if (
          field.type ===
            "datetime-local" &&
          typeof value ===
            "string"
        ) {
          value =
            value.slice(
              0,
              16
            );
        }

        next[
          field.name
        ] = value;

      }
    );

    setForm(
      next
    );

    setShowForm(
      true
    );

  };


  const closeForm = () => {

    if (
      saving
    ) {
      return;
    }

    setShowForm(
      false
    );

    setEditing(
      null
    );

    setError("");

  };


  /* =====================================================
     FORM VALUE
  ===================================================== */

  const changeValue = (
    name,
    value
  ) => {

    setForm(
      (
        current
      ) => ({
        ...current,
        [name]:
          value,
      })
    );

  };


  /* =====================================================
     SAVE
  ===================================================== */

  const submit =
    async (
      event
    ) => {

      event.preventDefault();

      setSaving(
        true
      );

      setError("");

      try {

        const payload =
          preparePayload(
            form,
            fields,
            Boolean(
              editing
            )
          );

        if (
          editing
        ) {

          await api.patch(
            `${endpoint}${editing.id}/`,
            payload
          );

        } else {

          await api.post(
            endpoint,
            payload
          );

        }

        setShowForm(
          false
        );

        setEditing(
          null
        );

        await loadRows();

        await loadOptions();

      } catch (
        error
      ) {

        const data =
          error.response
            ?.data;

        if (
          data &&
          typeof data ===
            "object"
        ) {

          setError(
            Object.entries(
              data
            )
              .map(
                ([
                  key,
                  value,
                ]) => {

                  const message =
                    Array.isArray(
                      value
                    )
                      ? value.join(
                          ", "
                        )
                      : typeof value ===
                          "object"
                        ? JSON.stringify(
                            value
                          )
                        : value;

                  return `${key}: ${message}`;

                }
              )
              .join(
                " | "
              )
          );

        } else {

          setError(
            "Unable to save record."
          );

        }

      } finally {

        setSaving(
          false
        );

      }

    };


  /* =====================================================
     DELETE
  ===================================================== */

  const remove =
    async (
      row
    ) => {

      const confirmed =
        window.confirm(
          "Are you sure you want to delete this record?"
        );

      if (
        !confirmed
      ) {
        return;
      }

      try {

        await api.delete(
          `${endpoint}${row.id}/`
        );

        await loadRows();

      } catch (
        error
      ) {

        setError(
          error.response
            ?.data?.detail ||
            "Unable to delete record."
        );

      }

    };


  /* =====================================================
     CUSTOM ACTION
  ===================================================== */

  const runAction =
    async (
      action,
      row
    ) => {

      if (
        action.confirm &&
        !window.confirm(
          action.confirm
        )
      ) {
        return;
      }

      try {

        await api({
          method:
            action.method ||
            "post",

          url:
            action.endpoint(
              row
            ),

          data:
            action.data
              ? action.data(
                  row
                )
              : undefined,
        });

        await loadRows();

      } catch (
        error
      ) {

        setError(
          error.response
            ?.data?.detail ||
            `Unable to ${action.label}.`
        );

      }

    };


  /* =====================================================
     FIELD
  ===================================================== */

  const renderField = (
    field
  ) => {

    const value =
      form[
        field.name
      ] ?? "";


    if (
      field.type ===
      "select"
    ) {

      const list =
        options[
          field.name
        ] || [];

      return (

        <select
          className="crud-form-control"
          value={
            value
          }
          required={
            field.required
          }
          disabled={
            field.readOnly
          }
          onChange={(
            event
          ) =>
            changeValue(
              field.name,
              event.target
                .value
            )
          }
        >

          <option value="">
            Select{" "}
            {field.label}
          </option>


          {field.options?.map(
            (
              option
            ) => (

              <option
                key={
                  option.value
                }
                value={
                  option.value
                }
              >
                {
                  option.label
                }
              </option>

            )
          )}


          {list.map(
            (
              option
            ) => (

              <option
                key={
                  option.id
                }
                value={
                  option.id
                }
              >

                {field.optionLabel
                  ? field.optionLabel(
                      option
                    )
                  : option.name ||
                    option.title ||
                    option.employee_code ||
                    option.id}

              </option>

            )
          )}

        </select>

      );

    }


    if (
      field.type ===
      "textarea"
    ) {

      return (

        <textarea
          className="crud-form-control"
          value={
            value
          }
          rows={3}
          required={
            field.required
          }
          onChange={(
            event
          ) =>
            changeValue(
              field.name,
              event.target
                .value
            )
          }
        />

      );

    }


    if (
      field.type ===
      "checkbox"
    ) {

      return (

        <div className="crud-checkbox-wrapper">

          <input
            type="checkbox"
            className="crud-checkbox"
            checked={
              Boolean(
                value
              )
            }
            onChange={(
              event
            ) =>
              changeValue(
                field.name,
                event.target
                  .checked
              )
            }
          />

          <span>
            {field.checkboxLabel ||
              field.label}
          </span>

        </div>

      );

    }


    return (

      <input
        type={
          field.type ||
          "text"
        }
        className="crud-form-control"
        value={
          value
        }
        required={
          field.required
        }
        min={
          field.min
        }
        max={
          field.max
        }
        step={
          field.step
        }
        readOnly={
          field.readOnly
        }
        onChange={(
          event
        ) =>
          changeValue(
            field.name,
            event.target
              .value
          )
        }
      />

    );

  };


  /* =====================================================
     PAGE
  ===================================================== */

  return (

    <div className="crud-page">


      <div className="crud-page-header">

        <div>

          <h1 className="crud-page-title">
            {title}
          </h1>

          <p className="crud-page-description">
            {description}
          </p>

        </div>


        <div className="crud-actions">

          <button
            type="button"
            className="crud-refresh-btn"
            onClick={
              loadRows
            }
          >

            <RefreshCw
              size={16}
            />

            Refresh

          </button>


          {allowCreate &&
            fields.length >
              0 && (

              <button
                type="button"
                className="crud-add-btn"
                onClick={
                  openCreate
                }
              >

                <Plus
                  size={17}
                />

                Add

              </button>

            )}

        </div>

      </div>


      {error &&
        !showForm && (

        <div className="crud-error">
          {error}
        </div>

      )}


      <div className="crud-card">


        <div className="crud-toolbar">

          <div className="crud-search-wrapper">

            <Search
              size={17}
              className="crud-search-icon"
            />

            <input
              type="text"
              className="crud-search"
              value={
                search
              }
              placeholder={`Search ${title.toLowerCase()}...`}
              onChange={(
                event
              ) => {

                setSearch(
                  event.target
                    .value
                );

                setPage(1);

              }}
            />

          </div>


          <span className="crud-record-count">

            {meta.count}{" "}

            {meta.count ===
            1
              ? "record"
              : "records"}

          </span>

        </div>


        <div className="crud-table-wrapper">

          <table className="crud-table">

            <thead>

              <tr>

                {columns.map(
                  (
                    column
                  ) => (

                    <th
                      key={
                        column.key
                      }
                    >
                      {
                        column.label
                      }
                    </th>

                  )
                )}


                {(allowEdit ||
                  allowDelete ||
                  rowActions.length >
                    0) && (

                  <th>
                    Actions
                  </th>

                )}

              </tr>

            </thead>


            <tbody>

              {loading ? (

                <tr>

                  <td
                    className="crud-empty"
                    colSpan={
                      columns.length +
                      1
                    }
                  >
                    Loading...
                  </td>

                </tr>

              ) : rows.length ===
                0 ? (

                <tr>

                  <td
                    className="crud-empty"
                    colSpan={
                      columns.length +
                      1
                    }
                  >
                    No records found.
                  </td>

                </tr>

              ) : (

                rows.map(
                  (
                    row
                  ) => (

                    <tr
                      key={
                        row.id
                      }
                    >

                      {columns.map(
                        (
                          column
                        ) => {

                          const value =
                            column.render
                              ? column.render(
                                  row
                                )
                              : row[
                                  column
                                    .key
                                ];

                          return (

                            <td
                              key={
                                column.key
                              }
                            >

                              {value ===
                              true
                                ? "Yes"
                                : value ===
                                  false
                                  ? "No"
                                  : value ??
                                    "—"}

                            </td>

                          );

                        }
                      )}


                      {(allowEdit ||
                        allowDelete ||
                        rowActions.length >
                          0) && (

                        <td>

                          <div className="crud-row-actions">

                            {rowActions.map(
                              (
                                action
                              ) => (

                                <button
                                  type="button"
                                  key={
                                    action.label
                                  }
                                  className={
                                    action.className ||
                                    "btn btn-sm btn-outline-success"
                                  }
                                  onClick={() =>
                                    runAction(
                                      action,
                                      row
                                    )
                                  }
                                >
                                  {
                                    action.label
                                  }
                                </button>

                              )
                            )}


                            {allowEdit &&
                              fields.length >
                                0 && (

                                <button
                                  type="button"
                                  className="crud-icon-btn crud-edit-btn"
                                  onClick={() =>
                                    openEdit(
                                      row
                                    )
                                  }
                                >

                                  <Edit3
                                    size={
                                      16
                                    }
                                  />

                                </button>

                              )}


                            {allowDelete && (

                              <button
                                type="button"
                                className="crud-icon-btn crud-delete-btn"
                                onClick={() =>
                                  remove(
                                    row
                                  )
                                }
                              >

                                <Trash2
                                  size={
                                    16
                                  }
                                />

                              </button>

                            )}

                          </div>

                        </td>

                      )}

                    </tr>

                  )
                )

              )}

            </tbody>

          </table>

        </div>


        {(meta.next ||
          meta.previous) && (

          <div className="crud-footer">

            <span>
              Page {page}
            </span>

            <div className="d-flex gap-2">

              <button
                type="button"
                className="btn btn-sm btn-outline-secondary"
                disabled={
                  !meta.previous
                }
                onClick={() =>
                  setPage(
                    (
                      current
                    ) =>
                      Math.max(
                        1,
                        current -
                          1
                      )
                  )
                }
              >
                Previous
              </button>

              <button
                type="button"
                className="btn btn-sm btn-outline-secondary"
                disabled={
                  !meta.next
                }
                onClick={() =>
                  setPage(
                    (
                      current
                    ) =>
                      current +
                      1
                  )
                }
              >
                Next
              </button>

            </div>

          </div>

        )}

      </div>


      {/* =================================================
          MODAL
      ================================================== */}

      {showForm && (

        <div
          className="crud-modal-backdrop"
          onMouseDown={
            closeForm
          }
        >

          <div
            className="crud-modal"
            onMouseDown={(
              event
            ) =>
              event.stopPropagation()
            }
          >

            <div className="crud-modal-header">

              <div>

                <h5 className="crud-modal-title">

                  {editing
                    ? `Edit ${title}`
                    : `Add ${title}`}

                </h5>

                <small className="text-muted">
                  Enter required
                  information.
                </small>

              </div>


              <button
                type="button"
                className="crud-modal-close"
                onClick={
                  closeForm
                }
              >

                <X
                  size={20}
                />

              </button>

            </div>


            <form
              onSubmit={
                submit
              }
            >

              <div className="crud-form">


                {error && (

                  <div className="crud-error">
                    {error}
                  </div>

                )}


                <div className="crud-form-grid">

                  {fields.map(
                    (
                      field
                    ) => (

                      <div
                        key={
                          field.name
                        }
                        className={`crud-form-group ${
                          field.fullWidth
                            ? "full-width"
                            : ""
                        }`}
                      >

                        {field.type !==
                          "checkbox" && (

                          <label className="crud-form-label">

                            {
                              field.label
                            }

                            {field.required && (

                              <span className="crud-required">
                                *
                              </span>

                            )}

                          </label>

                        )}


                        {renderField(
                          field
                        )}

                      </div>

                    )
                  )}

                </div>

              </div>


              <div className="crud-modal-footer">

                <button
                  type="button"
                  className="crud-cancel-btn"
                  onClick={
                    closeForm
                  }
                >
                  Cancel
                </button>


                <button
                  type="submit"
                  className="crud-save-btn"
                  disabled={
                    saving
                  }
                >

                  {saving
                    ? "Saving..."
                    : editing
                      ? "Update"
                      : "Save"}

                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </div>

  );
}